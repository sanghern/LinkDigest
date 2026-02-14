import React, { useState } from 'react';
import api from '../utils/api';

const AddBookmark = ({ onClose, onAdd, onDuplicateError }) => {
    const [formData, setFormData] = useState({
        url: '',          // 필수 입력
        title: '',        // 선택 입력
        tags: ''          // 선택 입력
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [duplicateError, setDuplicateError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setDuplicateError('');

        try {
            // URL이 비어있는지 확인
            if (!formData.url.trim()) {
                throw new Error('URL을 입력해주세요.');
            }

            // API 요청 데이터 준비
            const bookmarkData = {
                url: formData.url,
                // 선택 입력값은 값이 있을 때만 포함
                ...(formData.title.trim() && { title: formData.title }),
                ...(formData.tags.trim() && { 
                    tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                })
            };

            const response = await api.bookmarks.create(bookmarkData);
            onAdd(response);
            onClose();
        } catch (err) {
            if (err.response?.status === 409) {
                const message = '이미 동일한 URL이 저장되어 있습니다.';
                if (onDuplicateError) {
                    onDuplicateError(message);
                    onClose();
                } else {
                    setDuplicateError(message);
                }
            } else {
                setError(err.message || '북마크 추가에 실패했습니다.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center p-4 pt-8 sm:pt-12 lg:pt-16 z-50 overflow-y-auto">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] flex flex-col mt-4 sm:mt-8">
                {/* 상단 섹션 */}
                <div className="flex-none px-6 py-4 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-semibold text-gray-800">북마크 추가</h2>
                        <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* 중앙 컨텐츠 영역 */}
                <div className="flex-1 overflow-y-auto p-6">
                    {error && (
                        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
                            {error}
                        </div>
                    )}

                    {/* URL 중복 오류 팝업 */}
                    {duplicateError && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
                            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 border border-gray-200">
                                <h3 className="text-lg font-semibold text-gray-800 mb-2">URL 중복</h3>
                                <p className="text-gray-700 mb-4">{duplicateError}</p>
                                <div className="flex justify-end">
                                    <button
                                        type="button"
                                        onClick={() => setDuplicateError('')}
                                        className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700"
                                    >
                                        확인
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* URL 입력 필드 (필수) */}
                        <div>
                            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                                URL <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="url"
                                name="url"
                                id="url"
                                required
                                value={formData.url}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                placeholder="https://"
                            />
                        </div>

                        {/* 제목 입력 필드 (선택) */}
                        <div>
                            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                                제목 <span className="text-gray-400">(선택)</span>
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

                        {/* 키워드 입력 필드 (선택) */}
                        <div>
                            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
                                키워드 <span className="text-gray-400">(선택, 쉼표로 구분)</span>
                            </label>
                            <input
                                type="text"
                                name="tags"
                                id="tags"
                                value={formData.tags}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                placeholder="예: 기술, 프로그래밍, 자바스크립트"
                            />
                        </div>
                    </form>
                </div>

                {/* 하단 버튼 영역 */}
                <div className="flex-none px-6 py-4 border-t border-gray-200">
                    <div className="flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
                        >
                            취소
                        </button>
                        <button
                            type="submit"
                            onClick={handleSubmit}
                            disabled={loading}
                            className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? '처리중...' : '추가'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddBookmark; 