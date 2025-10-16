# Image Optimization Script

## Overview
This script optimizes store images for web use by resizing and compressing them.

## What it does
1. **Resizes images** to max 800x600px (maintains aspect ratio)
2. **Compresses PNG** files with quality optimization (80% quality)
3. **Creates WebP versions** for modern browsers (85% quality)
4. **Backs up originals** as `*.original.png` files

## Usage

### Quick start
```bash
node scripts/optimize-store-images.js
```

### Results
- **Before**: ~2.5-3.1 MB per PNG image (1536x1024px)
- **After PNG**: ~170-240 KB per PNG image (800x533px) - **92-94% smaller!**
- **After WebP**: ~60-90 KB per WebP image (800x533px) - **97-98% smaller!**

## What was optimized
All images matching `frontend/public/images/store*.png`:
- store.png
- store_atlanta_midtown.png
- store_austin_downtown.png
- store_boston_back_bay.png
- store_chicago_loop.png
- store_denver_lodo.png
- store_everett_station.png
- store_kirkland_waterfront.png
- store_miami_design_district.png
- store_nashville_music_row.png
- store_nyc_times_square.png
- store_phoenix_scottsdale.png
- store_pike_place.png
- store_spokane_pavilion.png

## File structure after optimization
```
frontend/public/images/
  ├── store.png                          (optimized PNG, ~170 KB)
  ├── store.original.png                 (backup, ~2.3 MB)
  ├── store.webp                         (WebP version, ~50 KB)
  ├── store_atlanta_midtown.png         (optimized PNG, ~214 KB)
  ├── store_atlanta_midtown.original.png (backup, ~2.7 MB)
  ├── store_atlanta_midtown.webp        (WebP version, ~88 KB)
  └── ... (same pattern for all store images)
```

## Using WebP in your frontend

### Option 1: Picture element (recommended)
```html
<picture>
  <source srcset="/images/store.webp" type="image/webp">
  <img src="/images/store.png" alt="Store">
</picture>
```

### Option 2: Vue component
```vue
<template>
  <picture>
    <source :srcset="`/images/${imageName}.webp`" type="image/webp">
    <img :src="`/images/${imageName}.png`" :alt="altText">
  </picture>
</template>
```

### Benefits of WebP
- 97-98% smaller than original PNGs
- 60-70% smaller than optimized PNGs
- Supported by all modern browsers
- Automatic fallback to PNG for older browsers

## Reverting changes
If you need to restore original images:
```bash
cd frontend/public/images
for file in *.original.png; do
  cp "$file" "${file%.original.png}.png"
done
```

## Re-running optimization
You can safely re-run the script. It will:
1. Use the current `.png` files (not the backups)
2. Create new backups
3. Regenerate optimized versions

## Dependencies
- **sharp**: Installed automatically by the script
- **Node.js**: v14+ required

## Configuration
Edit `scripts/optimize-store-images.js` to change:
- `MAX_WIDTH`: Maximum width (default: 800px)
- `MAX_HEIGHT`: Maximum height (default: 600px)
- `PNG_QUALITY`: PNG compression quality (default: 80)
- WebP quality is set to 85 in the script

## Performance impact
- **Page load time**: Reduced by ~2-2.5 MB per store image
- **Network bandwidth**: Reduced by 92-98% per image
- **Mobile performance**: Significantly improved on slow connections
- **SEO**: Better page speed scores

## Troubleshooting

### Error: Cannot find module 'sharp'
Run: `npm install sharp --save-dev`

### Error: EACCES permission denied
Run: `chmod +x scripts/optimize-store-images.js`

### Images look blurry
Increase `PNG_QUALITY` or `MAX_WIDTH/MAX_HEIGHT` in the script

### WebP not working in browser
- Ensure you're using the `<picture>` element for fallback
- Check browser compatibility (IE11 doesn't support WebP)
