// src/app/api/upload-image/route.js
import { NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

// Helper function to ensure the upload directory exists
async function ensureUploadDir() {
  const uploadDir = path.join(process.cwd(), 'public', 'uploads');
  try {
    await mkdir(uploadDir, { recursive: true });
    return uploadDir;
  } catch (error) {
    console.error('Error creating upload directory:', error);
    throw error;
  }
}

// Simple function to generate a unique filename without uuid
function generateUniqueFilename(originalName) {
  const timestamp = Date.now();
  const randomStr = Math.random().toString(36).substring(2, 8);
  const ext = originalName.split('.').pop();
  return `${timestamp}-${randomStr}.${ext}`;
}

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('image');
    
    if (!file) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Check file type
    if (!file.type.match('image.*')) {
      return NextResponse.json(
        { error: 'Invalid file type. Only images are allowed.' },
        { status: 400 }
      );
    }

    // Ensure upload directory exists
    const uploadDir = await ensureUploadDir();
    
    // Create a unique filename
    const buffer = Buffer.from(await file.arrayBuffer());
    const fileName = generateUniqueFilename(file.name);
    const filePath = path.join(uploadDir, fileName);
    
    // Write the file to disk
    await writeFile(filePath, buffer);
    
    // Generate the URL path that will be accessible from the browser
    const imagePath = `/uploads/${fileName}`;

    console.log('Image saved successfully at:', imagePath);

    return NextResponse.json({
      imagePath,
      success: true
    });
  } catch (error) {
    console.error('Error uploading image:', error);
    return NextResponse.json(
      { error: 'Failed to upload image: ' + error.message },
      { status: 500 }
    );
  }
}