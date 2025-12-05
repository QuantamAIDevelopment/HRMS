from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List, Optional
import os
import shutil

router = APIRouter()

# File upload endpoints removed