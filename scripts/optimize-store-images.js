#!/usr/bin/env node
/**
 * Optimize store images for web
 * - Resize to reasonable dimensions (800x600px max)
 * - Convert PNG to WebP with compression
 * - Also create optimized PNG versions (80% quality)
 * 
 * Usage: node optimize-store-images.js
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

const IMAGES_DIR = path.join(__dirname, '../frontend/public/images');
const MAX_WIDTH = 800;
const MAX_HEIGHT = 600;
const PNG_QUALITY = 80; // Quality for PNG compression

async function checkSharp() {
  try {
    require('sharp');
    return true;
  } catch (error) {
    return false;
  }
}

async function installSharp() {
  console.log('📦 Installing sharp...');
  try {
    execSync('npm install sharp --save-dev', { 
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit' 
    });
    console.log('✅ sharp installed successfully\n');
    return true;
  } catch (error) {
    console.error('❌ Failed to install sharp:', error.message);
    return false;
  }
}

async function optimizeWithSharp() {
  const sharp = require('sharp');
  
  // Find all store*.png files
  const files = await fs.readdir(IMAGES_DIR);
  const storeImages = files.filter(f => f.startsWith('store') && f.endsWith('.png'));
  
  console.log(`🖼️  Found ${storeImages.length} store images to optimize\n`);
  
  for (const filename of storeImages) {
    const inputPath = path.join(IMAGES_DIR, filename);
    const baseName = filename.replace('.png', '');
    
    try {
      const stats = await fs.stat(inputPath);
      const originalSizeMB = (stats.size / 1024 / 1024).toFixed(2);
      
      console.log(`Processing: ${filename} (${originalSizeMB} MB)`);
      
      // Get image metadata
      const metadata = await sharp(inputPath).metadata();
      console.log(`  Original: ${metadata.width}x${metadata.height}px`);
      
      // Calculate new dimensions while maintaining aspect ratio
      let newWidth = metadata.width;
      let newHeight = metadata.height;
      
      if (metadata.width > MAX_WIDTH) {
        newWidth = MAX_WIDTH;
        newHeight = Math.round((metadata.height / metadata.width) * MAX_WIDTH);
      }
      
      if (newHeight > MAX_HEIGHT) {
        newHeight = MAX_HEIGHT;
        newWidth = Math.round((metadata.width / metadata.height) * MAX_HEIGHT);
      }
      
      console.log(`  Resizing to: ${newWidth}x${newHeight}px`);
      
      // Create optimized PNG (backup original first)
      const backupPath = path.join(IMAGES_DIR, `${baseName}.original.png`);
      await fs.copyFile(inputPath, backupPath);
      console.log(`  ✅ Backup saved: ${baseName}.original.png`);
      
      // Optimize PNG - resize and compress
      await sharp(inputPath)
        .resize(newWidth, newHeight, {
          fit: 'inside',
          withoutEnlargement: true
        })
        .png({ quality: PNG_QUALITY, compressionLevel: 9 })
        .toFile(path.join(IMAGES_DIR, `${baseName}.optimized.png`));
      
      const pngStats = await fs.stat(path.join(IMAGES_DIR, `${baseName}.optimized.png`));
      const pngSizeMB = (pngStats.size / 1024 / 1024).toFixed(2);
      const pngSavings = (((stats.size - pngStats.size) / stats.size) * 100).toFixed(1);
      console.log(`  ✅ Optimized PNG: ${pngSizeMB} MB (${pngSavings}% smaller)`);
      
      // Create WebP version
      const webpPath = path.join(IMAGES_DIR, `${baseName}.webp`);
      await sharp(inputPath)
        .resize(newWidth, newHeight, {
          fit: 'inside',
          withoutEnlargement: true
        })
        .webp({ quality: 85 })
        .toFile(webpPath);
      
      const webpStats = await fs.stat(webpPath);
      const webpSizeMB = (webpStats.size / 1024 / 1024).toFixed(2);
      const webpSavings = (((stats.size - webpStats.size) / stats.size) * 100).toFixed(1);
      console.log(`  ✅ WebP version: ${webpSizeMB} MB (${webpSavings}% smaller)`);
      
      // Replace original with optimized version
      await fs.rename(path.join(IMAGES_DIR, `${baseName}.optimized.png`), inputPath);
      console.log(`  ✅ Original replaced with optimized version\n`);
      
    } catch (error) {
      console.error(`  ❌ Error processing ${filename}:`, error.message, '\n');
    }
  }
  
  console.log('🎉 Image optimization complete!');
  console.log('\n📝 Summary:');
  console.log('  - Original images backed up as *.original.png');
  console.log('  - PNG images optimized and replaced');
  console.log('  - WebP versions created as *.webp');
  console.log('\n💡 Tip: Update your frontend to use <picture> tags with WebP fallback for best results');
}

async function main() {
  console.log('🚀 Store Image Optimizer\n');
  
  // Check if sharp is available
  const hasSharp = await checkSharp();
  
  if (!hasSharp) {
    console.log('⚠️  sharp not found. Installing...\n');
    const installed = await installSharp();
    if (!installed) {
      console.error('\n❌ Cannot proceed without sharp. Please install manually:');
      console.error('   npm install sharp --save-dev\n');
      process.exit(1);
    }
  }
  
  await optimizeWithSharp();
}

main().catch(error => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
