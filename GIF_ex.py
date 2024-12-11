from PIL import Image

def gif_encs(path, paths_to_save:list, frames_to_cut:int=3) ->list:
    with Image.open(path) as gif:
        frames_count = gif.n_frames
        i = 0
        cnt = 0
        for j in range(len(paths_to_save)):          
            while cnt < frames_to_cut and i < frames_count:
                gif.seek(i)
                i += frames_count // (frames_to_cut - 1)
                cnt += 1
                gif.seek(frames_count - 1)
                frame = gif.convert('RGB')
                frame.save(paths_to_save[j])
        return paths_to_save


    