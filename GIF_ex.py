from PIL import Image
from loguru import logger

def gif_encs(path, paths_to_save:list, frames_to_cut:int=3) ->list:
    with Image.open(path) as gif:
        frames_count = gif.n_frames
        i = 0
        j=0
        cnt = 0  
        logger.debug(f"frames in file: {frames_count}")
        try:    
            while cnt < frames_to_cut and i < frames_count:
                    gif.seek(i)
                    i += frames_count // (frames_to_cut - 1)
                    cnt += 1
                    gif.seek(frames_count - 1)
                    frame = gif.convert('RGB')
                    frame.save(paths_to_save[j])
                    j+=1
            logger.success(f"images_save_complete from {paths_to_save}")          
            return paths_to_save
        except  ValueError as e:
            logger.error(f"{e} \n paths_to_save:{paths_to_save}")



    