from PIL import Image
from loguru import logger

def gif_encs(path, paths_to_save: list, frames_to_cut: int = 3) -> list:
    if len(paths_to_save) != frames_to_cut:
        raise ValueError("Количество путей для сохранения должно совпадать с количеством кадров для вырезки.")

    with Image.open(path) as gif:
        frames_count = gif.n_frames
        logger.debug(f"frames in file: {frames_count}")
        

        if frames_count < frames_to_cut:
            raise logger.error(f"В файле недостаточно кадров ({frames_count}) для вырезки {frames_to_cut} кадров.")

        for i in range(frames_to_cut):
            index = round((i / (frames_to_cut - 1)) * (frames_count - 1))
            gif.seek(index)
            frame = gif.convert('RGB')
            frame.save(paths_to_save[i])

        logger.success(f"Images saved to: {', '.join(paths_to_save)}")
        return paths_to_save



    