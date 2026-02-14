import React from 'react';
import { formatDate } from '../utils/dateUtils';

const DeleteBookmark = ({ bookmark, onClose, onDelete }) => {
    const handleDelete = async () => {
        try {
            await onDelete(bookmark.id);
            onClose();
        } catch (error) {
            console.error('북마크 삭제 실패:', error);
        }
    };

    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl relative">
                <div className="flex justify-between items-start mb-4">
                    <h2 className="text-2xl font-bold text-red-600">북마크 삭제</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="mb-6">
                    <div className="mb-4">
                        <h3 className="text-lg font-semibold mb-2">{bookmark.title}</h3>
                        {bookmark.summary && (
                            <p className="text-gray-600 mb-2 line-clamp-3">{bookmark.summary}</p>
                        )}
                        <div className="text-sm text-gray-500">
                            <p>생성일: {formatDate(bookmark.created_at)}</p>
                            {bookmark.updated_at && (
                                <p>수정일: {formatDate(bookmark.updated_at)}</p>
                            )}
                        </div>
                    </div>
                    <p className="text-red-600">이 북마크를 삭제하시겠습니까?</p>
                </div>

                <div className="flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                    >
                        취소
                    </button>
                    <button
                        onClick={handleDelete}
                        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                        삭제
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteBookmark; 