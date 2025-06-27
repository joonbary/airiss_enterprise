# app/db/repositories/file_repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.file_upload import FileUpload

class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_file_upload(self, file_data: dict) -> FileUpload:
        """파일 업로드 정보 저장"""
        file_upload = FileUpload(**file_data)
        self.session.add(file_upload)
        await self.session.commit()
        await self.session.refresh(file_upload)
        return file_upload
    
    async def get_file_upload(self, file_id: str) -> Optional[FileUpload]:
        """파일 정보 조회"""
        result = await self.session.execute(
            select(FileUpload).where(FileUpload.id == file_id)
        )
        return result.scalar_one_or_none()
    
    async def update_file_status(self, file_id: str, status: str):
        """파일 상태 업데이트"""
        file_upload = await self.get_file_upload(file_id)
        if file_upload:
            file_upload.status = status
            await self.session.commit()