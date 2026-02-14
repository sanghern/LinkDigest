import React, { useState } from 'react';
import api from '../utils/api';
import { formatDate } from '../utils/dateUtils';

const EditBookmark = ({ bookmark, onClose, onUpdate }) => {
    const [formData, setFormData] = useState({
        title: bookmark.title,
        url: bookmark.url,
        source_name: bookmark.source_name || '',
        summary: bookmark.summary || '',
        tags: bookmark.tags?.join(', ') || ''
    });
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const updatedBookmark = await api.bookmarks.update(bookmark.id, {
                ...formData,
                tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean)
            });
            onUpdate(updatedBookmark);
            onClose();
        } catch (err) {
            setError(err.message || '북마크 수정에 실패했습니다.');
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[95vh] flex flex-col">
                {/* 상단 섹션 */}
                <div className="flex-none px-6 py-4 border-b border-gray-200">
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <h2 className="text-xl font-semibold text-gray-800">북마크 수정</h2>
                        </div>
                        
                        {/* 버튼들을 상세보기와 같은 스타일로 배치 */}
                        <div className="flex items-center justify-between text-sm text-gray-500">
                            {/* 왼쪽: 메타 정보 */}
                            <div className="flex items-center space-x-4">
                                <span>{formatDate(bookmark.created_at)}</span>
                                <span>·</span>
                                <span>{bookmark.source_name || '-'}</span>
                            </div>

                            {/* 오른쪽: 버튼 그룹 */}
                            <div className="flex items-center space-x-2">
                                {/* 저장 버튼 */}
                                <button
                                    onClick={handleSubmit}
                                    className="text-blue-600 hover:text-blue-800"
                                    title="저장"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                </button>
                                
                                {/* 구분선 */}
                                <div className="h-4 w-px bg-gray-300"></div>
                                
                                {/* 취소 버튼 */}
                                <button
                                    onClick={onClose}
                                    className="text-gray-500 hover:text-gray-700"
                                    title="취소"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 폼 내용은 그대로 유지 */}
                <div className="flex-1 overflow-y-auto min-h-0 p-8">
                    <form className="space-y-6">
                        {error && (
                            <div className="mb-3 p-3 bg-red-100 text-red-700 rounded">
                                {error}
                            </div>
                        )}

                        <div className="flex gap-4">
                            <div className="flex-grow">
                                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                                    제목
                                </label>
                                <input
                                    type="text"
                                    name="title"
                                    id="title"
                                    value={formData.title}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                            </div>

                            <div className="w-1/3">
                                <label htmlFor="source_name" className="block text-sm font-medium text-gray-700 mb-1">
                                    출처
                                </label>
                                <input
                                    type="text"
                                    name="source_name"
                                    id="source_name"
                                    value={formData.source_name}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                                URL
                            </label>
                            <input
                                type="url"
                                name="url"
                                id="url"
                                value={formData.url}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            />
                        </div>

                        <div>
                            <label htmlFor="summary" className="block text-sm font-medium text-gray-700">
                                요약
                            </label>
                            <textarea
                                name="summary"
                                id="summary"
                                value={formData.summary}
                                onChange={handleChange}
                                rows="16"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            />
                        </div>

                        <div>
                            <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                                태그
                            </label>
                            <input
                                type="text"
                                name="tags"
                                id="tags"
                                value={formData.tags}
                                onChange={handleChange}
                                placeholder="쉼표로 구분하여 입력"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            />
                        </div>
                    </form>
                </div>

                {/* 하단 섹션 추가 */}
                <div className="flex-none px-6 py-4 border-t border-gray-200">
                    <div className="flex items-center justify-between text-sm text-gray-500">
                        <div>
                            <span className="font-medium">조회:</span> {bookmark.read_count || 0}회
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EditBookmark; 