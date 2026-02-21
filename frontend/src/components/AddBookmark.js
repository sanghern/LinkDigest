import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const AddBookmark = ({ onClose, onAdd, onDuplicateError }) => {
    const [formData, setFormData] = useState({
        url: '',             // URL 또는 아래 content 중 하나 입력
        content: '',         // 요약할 컨텐츠 직접 입력 (URL 미입력 시 사용)
        title: '',           // 선택 입력
        tags: '',            // 선택 입력
        summary_model: ''    // 요약에 사용할 모델 (선택)
    });
    const [modelList, setModelList] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [duplicateError, setDuplicateError] = useState('');

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const res = await api.bookmarks.getSummaryModels();
                const models = res?.models || [];
                setModelList(models);
                if (models.length > 0) {
                    setFormData(prev => ({ ...prev, summary_model: prev.summary_model || models[0] }));
                }
            } catch (e) {
                console.error('요약 모델 목록 로드 실패:', e);
            }
        };
        fetchModels();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setDuplicateError('');

        try {
            const hasUrl = formData.url.trim() !== '';
            const hasContent = formData.content.trim() !== '';
            if (!hasUrl && !hasContent) {
                throw new Error('URL 또는 요약할 컨텐츠를 입력해주세요.');
            }

            // API 요청 데이터 준비 (URL 입력 시 url 전송, 컨텐츠만 입력 시 content 전송)
            const bookmarkData = {
                ...(formData.title.trim() && { title: formData.title.trim() }),
                ...(formData.tags.trim() && {
                    tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                }),
                ...(formData.summary_model && { summary_model: formData.summary_model })
            };
            if (hasUrl) {
                bookmarkData.url = formData.url.trim();
            } else {
                bookmarkData.content = formData.content.trim();
            }

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
                        {/* URL 입력 필드 (URL 또는 아래 컨텐츠 중 하나 입력) */}
                        <div>
                            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                                URL <span className="text-gray-400">(또는 아래에 요약할 컨텐츠 입력)</span>
                            </label>
                            <input
                                type="url"
                                name="url"
                                id="url"
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

                        {/* 요약할 컨텐츠 직접 입력 (URL 미입력 시 사용) */}
                        <div>
                            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                                요약할 컨텐츠 <span className="text-gray-400">(URL 없이 입력 시 이 내용으로 Ollama 요약)</span>
                            </label>
                            <textarea
                                name="content"
                                id="content"
                                rows={5}
                                value={formData.content}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                placeholder="URL 대신 요약할 텍스트를 붙여넣으세요."
                            />
                        </div>

                        {/* 요약 모델 선택 */}
                        {modelList.length > 0 && (
                            <div>
                                <label htmlFor="summary_model" className="block text-sm font-medium text-gray-700 mb-1">
                                    요약 모델 <span className="text-gray-400">(선택)</span>
                                </label>
                                <select
                                    name="summary_model"
                                    id="summary_model"
                                    value={formData.summary_model || modelList[0]}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                >
                                    {modelList.map((m) => (
                                        <option key={m} value={m}>{m}</option>
                                    ))}
                                </select>
                            </div>
                        )}

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