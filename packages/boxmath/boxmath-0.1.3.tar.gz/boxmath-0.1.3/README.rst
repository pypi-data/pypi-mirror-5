===================================================================
boxmath
===================================================================

This provides image crop/resize algorithm for chaining multiple resize,
crop actions and producing a resulting crop/resize action pair.

-------------------------------------------------------------------
Usage
-------------------------------------------------------------------

The usage is fairly simple:

.. code:: python

    from boxmath import box, resize, crop, size, make_transformer
    from wand import image
    
    # Load the image to get its width and height
    i = image.Image(filename="chrysanthemum.jpg")
    b = box(i.width, i.height)
    
    # manipulate the virtual image
    b = resize(b, 629, 483)
    b = crop(b, 0, 0, 480, 480)
    b = resize(b, 1000, 1000)
    
    # render
    def resizer(img, w, h):
        img.resize(int(w), int(h), filter=FILTER)
        return img

    def cropper(img, l,t,r,b):
        img.crop(int(l),int(t),int(r),int(b))
        return img
    
    t = make_transformer(b, resizer, cropper)
    i = t(i)
    i.save(filename="chrysanthemum-1000x1000.jpg")


Normally, if we would of used wand or PIL directly, each resize would
degrade the image.  The action of down scaling and then up scaling
would wreck the quality of the image; with the power of math, we
only apply the resize and crop when we need render the image.

Not that the width, height, left, top, right, and bottom values
passed to the resizer and cropper functions are cast as ints.

This is because they are either fractions.Fraction() instances or
int().  `boxmath` uses the Fraction class to ensure precision while
resizing and cropping.


