import os
import platform
import psutil
import torch
import whisper
from pathlib import Path
from videodub.utils.select_model import select_optimal_model
from videodub import config
from transformers import pipeline
import ffmpeg
import warnings
warnings.filterwarnings("ignore")

def generate_subtitles(video_path, src_lang=config.DEFAULT_SRC_LANG, tgt_lang=config.DEFAULT_TGT_LANG, use_en_as_intermediate=config.DEFAULT_USE_EN_AS_INTERMEDIATE):
    """
    主函数：生成字幕文件。
    
    参数:
        video_path: 视频文件路径
        src_lang: 原始语言代码 (默认为日语 'ja')
        tgt_lang: 目标语言代码 (默认为中文 'zh')
    """
    # 1. 智能选择模型
    model_size = select_optimal_model()
    print(f"正在加载模型: {model_size}")
    
    # 2. 加载Whisper模型
    # 对于macOS Apple Silicon，可启用GPU加速
    if platform.system().lower() == "darwin" and platform.processor() == "arm":
        # 在某些情况下，MPS后端可能导致数值不稳定，可以考虑强制使用CPU
        device = "cpu"  # 强制使用CPU以避免NaN值问题
        # device = "mps"  # 如果MPS工作正常，可以取消注释此行
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    model = whisper.load_model(model_size, device=device)
    
    # 3. 提取音频 (使用FFmpeg)
    print("正在提取音频...")
    audio_path = config.TEMP_AUDIO_FILE
    # 使用os.path模块处理路径，确保跨平台兼容性
    video_path = os.path.abspath(video_path)
    
    # 使用ffmpeg-python for more precise audio extraction with proper timing
    try:
        # Extract audio with exact timing preservation
        stream = ffmpeg.input(video_path, ss=None, t=None)  # No seeking, full duration
        stream = ffmpeg.output(
            stream, 
            audio_path, 
            acodec='pcm_s16le',  # Use PCM for highest quality
            ac=1,               # Mono
            ar=config.AUDIO_SAMPLE_RATE,  # Sample rate
            vn=None,            # No video
            f='wav',            # Explicitly specify format
            loglevel='error',   # Reduce output verbosity
            copyts=True           # Copy timestamps to maintain sync
        )
        # Run the conversion
        ffmpeg.run(stream, overwrite_output=True, quiet=True, capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print(f"FFmpeg error during audio extraction: {e}")
        # Fallback to the original method if ffmpeg-python fails
        os.system(f'ffmpeg -i "{video_path}" -ar {config.AUDIO_SAMPLE_RATE} -ac 1 -y -loglevel error -copyts "{audio_path}"')
    
    # 4. 语音识别与翻译
    print("正在识别语音...")
    # 首先进行语音识别，不管是否需要翻译
    transcription_result = model.transcribe(audio_path, language=src_lang, task="transcribe")
    
    # 如果源语言和目标语言不同，则进行翻译
    if src_lang != tgt_lang:
        print(f"正在将{src_lang}翻译为{tgt_lang}...")
        print(f"注意：Whisper目前仅支持将语音翻译成英文。如需其他语言翻译，需要额外的文本翻译模型。\n当前实现会先进行语音识别，然后根据设置决定是否通过英语中转实现多语言翻译。")
        
        # 使用Whisper进行语音识别
        result = transcription_result
        
        # 尝试使用HuggingFace翻译模型进行文本翻译
        try:
            # 首先尝试直接翻译
            direct_model = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
            translator = None
            
            try:
                print(f"尝试加载直接翻译模型: {direct_model}")
                translator = pipeline("translation", model=direct_model, device="cpu")
                print(f"成功加载直接翻译模型: {direct_model}")
                
                # 对每个文本片段进行翻译
                for i in range(len(result['segments'])):
                    original_text = result['segments'][i]['text'].strip()  # type: ignore
                    if original_text:
                        try:
                            translation = translator(original_text)
                            translated_text = translation[0]['translation_text'] if isinstance(translation, list) and len(translation) > 0 else str(translation)
                            result['segments'][i]['text'] = translated_text  # type: ignore
                        except Exception as e:
                            print(f"翻译文本片段时出错: {str(e)}，保留原文")
                            pass  # 如果翻译失败，保留原文
            except Exception as e:
                print(f"直接翻译模型加载失败: {str(e)}")
                
                # 如果启用了英语中转且目标语言不是英语，则尝试通过英语中转
                if use_en_as_intermediate and tgt_lang != 'en':
                    print("尝试通过英语中转翻译...")
                    
                    # 尝试从源语言翻译到英语
                    src_to_en_model = f"Helsinki-NLP/opus-mt-{src_lang}-en"
                    src_to_en_translator = None
                    try:
                        print(f"尝试加载源语言到英语翻译模型: {src_to_en_model}")
                        src_to_en_translator = pipeline("translation", model=src_to_en_model, device="cpu")
                        print(f"成功加载源语言到英语翻译模型: {src_to_en_model}")
                    except Exception as e1:
                        print(f"源语言到英语翻译模型加载失败: {str(e1)}")
                        # 尝试使用多语言到英语的模型
                        try:
                            print("尝试加载多语言到英语翻译模型: Helsinki-NLP/opus-mt-mul-en")
                            src_to_en_translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en", device="cpu")
                            print("成功加载多语言到英语翻译模型")
                        except Exception as e2:
                            print(f"所有英语翻译模型都加载失败: {str(e2)}")
                            print(f"回退到Whisper内置翻译（仅限英语）")
                            result = model.transcribe(audio_path, language=src_lang, task="translate")
                            return  # 直用返回，不进行进一步翻译
                
                    # 尝试从英语翻译到目标语言
                    en_to_tgt_model = f"Helsinki-NLP/opus-mt-en-{tgt_lang}"
                    try:
                        print(f"尝试加载英语到目标语言翻译模型: {en_to_tgt_model}")
                        en_to_tgt_translator = pipeline("translation", model=en_to_tgt_model, device="cpu")
                        print(f"成功加载英语到目标语言翻译模型: {en_to_tgt_model}")
                        
                        # 执行两步翻译：源语言 -> 英语 -> 目标语言
                        for i in range(len(result['segments'])):
                            original_text = result['segments'][i]['text'].strip()  # type: ignore
                            if original_text:
                                try:
                                    # 第一步：源语言 -> 英语
                                    en_translation = src_to_en_translator(original_text)
                                    en_text = en_translation[0]['translation_text'] if isinstance(en_translation, list) and len(en_translation) > 0 else str(en_translation)
                                    
                                    # 第二步：英语 -> 目标语言
                                    final_translation = en_to_tgt_translator(en_text)
                                    final_text = final_translation[0]['translation_text'] if isinstance(final_translation, list) and len(final_translation) > 0 else str(final_translation)
                                    
                                    result['segments'][i]['text'] = final_text  # type: ignore
                                except Exception as e:
                                    print(f"两步翻译失败: {str(e)}，保留原文")
                                    pass  # 如果翻译失败，保留原文
                    except Exception as e3:
                        print(f"英语到目标语言翻译模型加载失败: {str(e3)}")
                        print(f"仅使用源语言到英语的翻译")
                        # 只进行源语言到英语的翻译
                        for i in range(len(result['segments'])):
                            original_text = result['segments'][i]['text'].strip()  # type: ignore
                            if original_text:
                                try:
                                    translation = src_to_en_translator(original_text)
                                    translated_text = translation[0]['translation_text'] if isinstance(translation, list) and len(translation) > 0 else str(translation)
                                    result['segments'][i]['text'] = translated_text  # type: ignore
                                except Exception as e:
                                    print(f"翻译失败: {str(e)}，保留原文")
                                    pass  # 如果翻译失败，保留原文
                else:
                    print(f"直接翻译模型不可用，且未启用英语中转（use_en_as_intermediate={use_en_as_intermediate}），将使用Whisper的内置翻译（仅限英语）")
                    # 重新运行Whisper，但这次使用translate任务
                    result = model.transcribe(audio_path, language=src_lang, task="translate")
        except Exception as e:
            print(f"文本翻译失败 ({str(e)})，回退到Whisper内置翻译（仅限英语）")
            result = model.transcribe(audio_path, language=src_lang, task="translate")
    else:
        result = transcription_result
    
    # 5. 生成字幕文件
    video_dir = os.path.dirname(video_path)
    video_name = Path(video_path).stem
    output_srt_path = os.path.join(video_dir, f"{video_name}_{tgt_lang}.srt")
    
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result["segments"], 1):
            start = segment["start"]  # type: ignore
            end = segment["end"]  # type: ignore
            text = segment["text"].strip()  # type: ignore
            # 格式化时间戳并写入SRT文件
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")
    
    # 6. 清理临时文件
    os.remove(audio_path)
    print(f"字幕生成完成: {output_srt_path}")

def format_timestamp(seconds):
    """将秒数格式化为SRT标准时间戳 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"