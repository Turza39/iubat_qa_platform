"""
Supabase storage utilities for file uploads.

This module provides functions to upload files to Supabase Storage
and retrieve their public URLs.
"""
import os
import uuid
from typing import Optional

import httpx

from config import settings


def get_supabase_client(service_role: bool = False) -> httpx.Client:
    """
    Returns an HTTP client configured for Supabase Storage API.
    
    Args:
        service_role: If True, uses the service role key (for uploads/deletes).
                      If False, uses the anon key (for public reads).
    """
    if not settings.SUPABASE_URL:
        raise ValueError("Supabase configuration is missing. Check SUPABASE_URL.")
    
    # Use service role key for admin operations (upload/delete)
    # Use anon key for public operations (read)
    api_key = settings.SUPABASE_SECRET_KEY if service_role else settings.SUPABASE_ACCESS_KEY
    
    if not api_key:
        raise ValueError("Supabase API key missing")

    return httpx.Client(
        headers={
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        },
        timeout=30.0,
    )


async def upload_to_supabase(
    file_content: bytes,
    filename: str,
    content_type: str,
    folder: Optional[str] = None
) -> str:
    """
    Upload a file to Supabase Storage and return the public URL.

    Args:
        file_content: The binary content of the file
        filename: Original filename (will be sanitized)
        content_type: MIME type of the file
        folder: Optional subfolder within the bucket

    Returns:
        Public URL of the uploaded file

    Raises:
        ValueError: If Supabase is not configured
        httpx.HTTPError: If the upload fails
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ACCESS_KEY:
        raise ValueError("Supabase is not configured")

    # Sanitize filename - keep only safe characters
    safe_name = "".join(c for c in os.path.basename(filename) if c.isalnum() or c in ".-_")
    
    # Generate unique filename to avoid collisions
    ext = os.path.splitext(safe_name)[1] if "." in safe_name else ""
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Build the storage path
    storage_path = f"{folder}/{unique_filename}" if folder else unique_filename

    # Supabase Storage REST API endpoint
    storage_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{storage_path}"

    client = get_supabase_client(service_role=True)
    
    try:
        response = client.post(
            storage_url,
            content=file_content,
            headers={
                "Content-Type": content_type,
                "x-upsert": "true",  # Allow overwriting if exists
            }
        )
        response.raise_for_status()
        
        # Build public URL
        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{storage_path}"
        return public_url
        
    except httpx.HTTPError as e:
        raise httpx.HTTPError(f"Failed to upload file to Supabase: {e}") from e
    finally:
        client.close()


async def delete_from_supabase(file_url: str) -> bool:
    """
    Delete a file from Supabase Storage.

    Args:
        file_url: The public URL of the file to delete

    Returns:
        True if deletion was successful

    Raises:
        ValueError: If Supabase is not configured
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ACCESS_KEY:
        raise ValueError("Supabase is not configured")

    # Extract the storage path from the URL
    # URL format: https://xxx.supabase.co/storage/v1/object/public/bucket-name/path/to/file
    bucket_path = "/storage/v1/object/public/"
    if bucket_path not in file_url:
        return False

    try:
        storage_path = file_url.split(bucket_path)[1]
        # Remove bucket name from path
        if "/" in storage_path:
            storage_path = "/".join(storage_path.split("/")[1:])
    except IndexError:
        return False

    storage_url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{storage_path}"
    
    client = get_supabase_client(service_role=True)
    
    try:
        response = client.delete(storage_url)
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False
    finally:
        client.close()


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return bool(
        settings.SUPABASE_URL 
        and settings.SUPABASE_ACCESS_KEY 
        and settings.SUPABASE_BUCKET
    )