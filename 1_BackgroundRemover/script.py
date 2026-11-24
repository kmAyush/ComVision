import cv2
import numpy as np
from numpy.typing import NDArray

colored_image = cv2.imread('inputs/internetImg.png')
image = cv2.cvtColor(colored_image, cv2.COLOR_BGR2GRAY)
H,W = image.shape

def get_background(img: NDArray[np.int8]) -> np.float32:
    H,W = img.shape
    image = cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    
    h,w = image.shape
    k_size = int(max(h,w)*0.05)
    k_size = max(3, k_size if k_size % 2 == 1 else k_size+1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_size, k_size))
    
    # Morph close Dillation then Erosion
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    success = cv2.imwrite('outputs/step1_morph_close.png', image)

    image = cv2.medianBlur(image, 31)
    success = cv2.imwrite('outputs/step2_medianBlur.png', image)
    image = cv2.GaussianBlur(image, (21,21), 0)
    success = cv2.imwrite('outputs/step3_GaussianBlur.png', image)
    image = cv2.resize(image, (W,H), interpolation=cv2.INTER_LINEAR)
    success = cv2.imwrite('outputs/step4_background.png', image)
    
    background = np.maximum(image.astype(np.float32), 1.0)
    return background

if image is None:
    print("Error: Could not load image. Check the file path")
else:
    background = get_background(image)
    background = np.maximum(background,1.0)
    flat = image/background
    flat = np.clip(flat,0.0,1.0)
    flat_img = (flat*255).astype(np.uint8)
    flat_save = cv2.imwrite('outputs/step5_flat_img.png', flat_img)

    paper_level = np.percentile(flat, 90)
    ink_level = np.percentile(flat,1.0)
    print("Paper_Level", paper_level)
    print("Ink_level", ink_level)

    adjusted_paper = paper_level-0.03
    denom = max(adjusted_paper-ink_level, 1e-6)

    alpha = (adjusted_paper - flat) / denom
    alpha = (np.clip(alpha, 0, 1)*255).astype(np.uint8)
    alpha_save = cv2.imwrite('outputs/step6_alpha_img.png',alpha)
    
    # Step 5: Extract Ink Color
    ink_mask = alpha > 0.8
    ink_pixels = colored_image[ink_mask]
    
    if ink_pixels.size > 0:
        ink_color = np.median(ink_pixels, axis=0)
    else:
        ink_color = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    ink_color_uint8 = np.round(ink_color).astype(np.uint8)
    print("Ink Color:", ink_color_uint8)
    
    final_img = np.empty((H,W,4), dtype=np.uint8)
    final_img[:,:,:3] = np.round(ink_color).astype(np.uint8)
    final_img[:,:,3] = np.clip(np.round(alpha*255.0),0,255).astype(np.uint8)
    
    k_size = int(max(H,W)*0.05)
    k_size = max(3, k_size if k_size % 2 == 1 else k_size+1)

   
    # final_img = cv2.medianBlur(final_img, 15)

    cv2.imwrite("outputs/step7_result.png", final_img)
    

    for i in range(10):
        for j in range(10):
            print(final_img[i][j], end=" ")
        print()
