from PIL import Image

def gif_encs(path, paths_to_save:list) ->list:
    with Image.open(path) as gif:
        frames_count = gif.n_frames
        print(frames_count)

        gif.seek(0)  # go to first frame
        first_frame = gif.convert('RGB')
        first_frame.save(paths_to_save[0])
        
        gif.seek(frames_count//2)
        second_frame = gif.convert("RGB")
        second_frame.save(paths_to_save[1])

        gif.seek(frames_count - 1) 
        final_frame = gif.convert('RGB')    
        final_frame.save(paths_to_save[2])
    return paths_to_save


    