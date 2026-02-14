import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import AddBookmark from './AddBookmark';
import EditBookmark from './EditBookmark';
import BookmarkDetail from './BookmarkDetail';
import ErrorMessage from './ErrorMessage';
import DeleteBookmark from './DeleteBookmark';
import { formatDate } from '../utils/dateUtils';
import LoadingSpinner from './LoadingSpinner';

// eslint-disable-next-line no-unused-vars
const EllipsisIcon = () => (
    <svg className="h-5 w-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
    </svg>
);

const BookmarkList = () => {
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [showDuplicateErrorModal, setShowDuplicateErrorModal] = useState(false);
    const [duplicateErrorMessage, setDuplicateErrorMessage] = useState('');
    const [selectedBookmark, setSelectedBookmark] = useState(null);
    const [showDetail, setShowDetail] = useState(false);
    const [showEdit, setShowEdit] = useState(false);
    const [showDelete, setShowDelete] = useState(false);
    
    // 페이지네이션 상태 관리
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    // totalItems는 실제로 사용되므로 유지하되 total_pages 계산에 사용
    // eslint-disable-next-line no-unused-vars
    const [totalItems, setTotalItems] = useState(0);
    const ITEMS_PER_PAGE = 10;
    
    // 키워드 검색 상태 관리 (다중 선택 지원)
    const [selectedTags, setSelectedTags] = useState([]);

    // fetchBookmarks를 useCallback으로 메모이제이션
    const fetchBookmarks = useCallback(async () => {
        try {
            setLoading(true);
            // 여러 키워드를 배열로 전달 (AND 조건으로 검색됨)
            const tagsParam = selectedTags.length > 0 ? selectedTags : undefined;
            
            // 디버깅: 전달되는 파라미터 확인
            console.log('[Frontend] fetchBookmarks 호출:', {
                page: currentPage,
                per_page: ITEMS_PER_PAGE,
                tags: tagsParam,
                selectedTags: selectedTags
            });
            
            const response = await api.bookmarks.getList({
                page: currentPage,
                per_page: ITEMS_PER_PAGE,
                tags: tagsParam
            });
            
            const { items, total, total_pages } = response;
            
            setBookmarks(items);
            setTotalItems(total);
            setTotalPages(total_pages);
        } catch (err) {
            setError('북마크 목록을 불러오는데 실패했습니다.');
            console.error('북마크 목록 조회 실패:', err);
            setBookmarks([]);
            setTotalPages(1);
            setTotalItems(0);
        } finally {
            setLoading(false);
        }
    }, [currentPage, ITEMS_PER_PAGE, selectedTags]);

    // 페이지 변경 핸들러 개선
    const handlePageChange = (page) => {
        if (page !== currentPage) {
            setCurrentPage(page);
            // 페이지 변경 시 스크롤을 상단으로 이동
            window.scrollTo(0, 0);
        }
    };

    // 키워드 클릭 핸들러 (다중 선택/제거 지원)
    const handleTagClick = (e, tag) => {
        e?.stopPropagation();
        setSelectedTags(prev => {
            // 이미 선택된 키워드면 제거, 없으면 추가
            if (prev.includes(tag)) {
                return prev.filter(t => t !== tag);
            } else {
                return [...prev, tag];
            }
        });
        setCurrentPage(1); // 검색 시 첫 페이지로 이동
    };

    // 개별 키워드 제거 핸들러
    const handleRemoveTag = (e, tagToRemove) => {
        e?.stopPropagation();
        setSelectedTags(prev => prev.filter(t => t !== tagToRemove));
        setCurrentPage(1);
    };

    // 검색 필터 전체 초기화 핸들러
    const handleClearFilter = () => {
        setSelectedTags([]);
        setCurrentPage(1);
    };

    // 페이지 변경 시 데이터 다시 로드
    useEffect(() => {
        fetchBookmarks();
    }, [currentPage, fetchBookmarks]);

    const handleDelete = async (id) => {
        try {
            await api.bookmarks.delete(id);
            
            // 현재 페이지의 마지막 아이템을 삭제하는 경우
            if (bookmarks.length === 1 && currentPage > 1) {
                // 이전 페이지로 이동
                setCurrentPage(prev => prev - 1);
            } else {
                // 현재 페이지 새로고침
                fetchBookmarks();
            }
        } catch (err) {
            setError('북마크 삭제에 실패했습니다.');
            console.error('북마크 삭제 실패:', err);
        }
    };

    const handleUpdate = (updatedBookmark) => {
        fetchBookmarks();
    };

    const handleAdd = async (newBookmark) => {
        try {
            // 북마크 추가 후 항상 첫 페이지로 이동
            setCurrentPage(1);
            await fetchBookmarks();
            setShowAddModal(false);
        } catch (err) {
            setError('북마크 목록 갱신에 실패했습니다.');
            console.error('북마크 목록 갱신 실패:', err);
        }
    };

    // eslint-disable-next-line no-unused-vars
    const handleViewClick = async (e, bookmark) => {
        e.stopPropagation();
        if (!bookmark?.id) {
            console.error('유효하지 않은 북마크');
            return;
        }

        try {
            const updatedBookmark = await api.bookmarks.getById(bookmark.id);
            if (updatedBookmark) {
                setSelectedBookmark(updatedBookmark);
                setShowDetail(true);
            }
        } catch (error) {
            console.error('북마크 상세 정보 조회 실패:', error);
            setError('북마크 상세 정보를 불러오는데 실패했습니다.');
        }
    };

    // eslint-disable-next-line no-unused-vars
    const handleEditClick = (e, bookmark) => {
        e.stopPropagation();
        setSelectedBookmark(bookmark);
        setShowEdit(true);
    };

    // eslint-disable-next-line no-unused-vars
    const handleDeleteClick = (e, bookmark) => {
        e.stopPropagation();
        setSelectedBookmark(bookmark);
        setShowDelete(true);
    };

    // eslint-disable-next-line no-unused-vars
    const handleTitleClick = async (e, bookmark) => {
        e.preventDefault();
        try {
            const updatedBookmark = await api.bookmarks.getById(bookmark.id);
            setSelectedBookmark(updatedBookmark);
            setShowDetail(true);
        } catch (error) {
            console.error('북마크 상세 정보 조회 실패:', error);
            setError('북마크 상세 정보를 불러오는데 실패했습니다.');
        }
    };

    // 북마크 목록 새로고침 함수
    const refreshBookmarks = useCallback(async () => {
        try {
            // 토큰 유효성 먼저 확인
            await api.auth.me();  // 현재 사용자 정보 확인
            await fetchBookmarks();
        } catch (error) {
            if (error.response?.status === 401) {
                // 토큰이 만료된 경우 로그인 페이지로 리다이렉트
                window.location.href = '/login';
            } else {
                console.error('북마크 목록 새로고침 실패:', error);
                setError('북마크 목록을 새로고침하는데 실패했습니다.');
            }
        }
    }, [fetchBookmarks]);

    // 상세보기 닫기 핸들러 수정
    const handleDetailClose = async (openEdit = false, pageToChange = null) => {  // openEdit, pageToChange 파라미터 추가
        setShowDetail(false);
        if (openEdit) {
            // 수정 모달 열기
            setShowEdit(true);
        } else {
            setSelectedBookmark(null);
        }
        
        // 페이지 변경이 요청된 경우 먼저 페이지 변경
        if (pageToChange !== null && pageToChange !== currentPage) {
            // 페이지를 변경하면 useEffect가 자동으로 fetchBookmarks를 호출함
            setCurrentPage(pageToChange);
            // 스크롤을 상단으로 이동
            window.scrollTo(0, 0);
        } else {
            // 페이지 변경이 없는 경우에만 새로고침
            await refreshBookmarks();
        }
    };

    if (loading) return <div className="text-center py-4">로딩 중...</div>;

    // 상세보기가 열려있으면 상세보기만 표시
    if (showDetail && selectedBookmark) {
        return (
            <div className="w-full px-2 sm:px-4 lg:px-6 xl:px-12 2xl:px-16 py-4 sm:py-8">
                <div className="w-full mx-auto">
                    <BookmarkDetail
                        bookmark={selectedBookmark}
                        onClose={handleDetailClose}
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={handlePageChange}
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="w-full px-2 sm:px-4 lg:px-8 py-4 sm:py-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 sm:mb-6 gap-3 sm:gap-0">
                    <div className="flex items-center gap-3 flex-wrap">
                        <h1 className="text-lg sm:text-xl font-bold">
                            북마크 요약{totalItems > 0 && `(${totalItems}개)`}
                        </h1>
                        {selectedTags.length > 0 && (
                            <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-sm text-gray-600">필터:</span>
                                {selectedTags.map((tag, idx) => (
                                    <span 
                                        key={idx}
                                        className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded flex items-center gap-1"
                                    >
                                        {tag}
                                        <button
                                            onClick={(e) => handleRemoveTag(e, tag)}
                                            className="text-blue-600 hover:text-blue-800 text-sm ml-1"
                                            title={`${tag} 필터 제거`}
                                        >
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </span>
                                ))}
                                <button
                                    onClick={handleClearFilter}
                                    className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
                                    title="모든 필터 제거"
                                >
                                    전체 제거
                                </button>
                            </div>
                        )}
                    </div>
                    <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
                        {/* 상단 페이지네이션 */}
                        {totalPages > 1 && (
                            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[8px] sm:text-[10px] order-2 sm:order-1">
                                {/* 이전 페이지 버튼 */}
                                <button
                                    onClick={() => handlePageChange(currentPage - 1)}
                                    disabled={currentPage === 1}
                                    className={`relative inline-flex items-center px-1.5 sm:px-2 py-1.5 sm:py-2 rounded-l-md border text-[8px] sm:text-[10px] font-medium ${
                                        currentPage === 1
                                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                            : 'bg-white text-gray-500 hover:bg-gray-50'
                                    }`}
                                >
                                    이전
                                </button>

                                {/* 페이지 번호 */}
                                {[...Array(totalPages)].map((_, i) => (
                                    <button
                                        key={i + 1}
                                        onClick={() => handlePageChange(i + 1)}
                                        className={`relative inline-flex items-center px-2 sm:px-4 py-1.5 sm:py-2 border text-[8px] sm:text-[10px] font-medium ${
                                            currentPage === i + 1
                                                ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                        }`}
                                    >
                                        {i + 1}
                                    </button>
                                ))}

                                {/* 다음 페이지 버튼 */}
                                <button
                                    onClick={() => handlePageChange(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                    className={`relative inline-flex items-center px-1.5 sm:px-2 py-1.5 sm:py-2 rounded-r-md border text-[8px] sm:text-[10px] font-medium ${
                                        currentPage === totalPages
                                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                            : 'bg-white text-gray-500 hover:bg-gray-50'
                                    }`}
                                >
                                    다음
                                </button>
                            </nav>
                        )}
                        {/* 새 북마크 버튼 */}
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="bg-blue-500 text-white px-3 py-1.5 rounded hover:bg-blue-600 text-xs sm:text-sm w-full sm:w-auto order-1 sm:order-2"
                        >
                            새 북마크
                        </button>
                    </div>
                </div>

            {error && <ErrorMessage message={error} />}

            {loading ? (
                <LoadingSpinner />
            ) : (
                <>
                    {/* 북마크 목록 - 카드 형태로 변경 */}
                    <div className="grid gap-3 sm:gap-4">
                        {bookmarks.map(bookmark => (
                            <div key={bookmark.id} className="bg-white rounded-lg shadow p-3 sm:p-4">
                                {/* 북마크 제목 */}
                                <h3 
                                    className="text-sm sm:text-base font-semibold cursor-pointer hover:text-blue-600 break-words"
                                    onClick={(e) => handleTitleClick(e, bookmark)}
                                >
                                    {bookmark.title}
                                </h3>

                                {/* 메타 정보와 액션 버튼 */}
                                <div className="mt-2 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 sm:gap-0">
                                    {/* 메타 정보 */}
                                    <div className="text-xs sm:text-sm text-gray-500 flex flex-wrap items-center gap-1 sm:gap-2 flex-grow">
                                        {/* 태그/키워드 */}
                                        {bookmark.tags && bookmark.tags.length > 0 && (
                                            <>
                                                <div className="flex items-center flex-wrap gap-1">
                                                    {bookmark.tags.map((tag, idx) => {
                                                        const isSelected = selectedTags.includes(tag);
                                                        return (
                                                            <span 
                                                                key={idx} 
                                                                onClick={(e) => handleTagClick(e, tag)}
                                                                className={`text-xs px-1.5 sm:px-2 py-0.5 rounded cursor-pointer transition-colors ${
                                                                    isSelected 
                                                                        ? 'bg-blue-500 text-white hover:bg-blue-600' 
                                                                        : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                                                                }`}
                                                                title={isSelected ? `${tag} 필터 제거` : `${tag} 필터 추가`}
                                                            >
                                                                {tag}
                                                            </span>
                                                        );
                                                    })}
                                                </div>
                                                <span className="hidden sm:inline text-gray-300">|</span>
                                            </>
                                        )}
                                        <span className="hidden sm:inline text-gray-300">|</span>
                                        <span>조회수: {bookmark.read_count || 0}</span>
                                        <span className="text-gray-300">|</span>
                                        <span className="text-xs sm:text-sm">{formatDate(bookmark.created_at)}</span>
                                        <span className="text-gray-300">|</span>
                                        <span className="text-xs sm:text-sm truncate max-w-[100px] sm:max-w-none">{bookmark.source_name || '-'}</span>
                                    </div>

                                    {/* 액션 버튼들 */}
                                    <div className="flex items-center space-x-2 sm:space-x-3 ml-0 sm:ml-4">
                                        {/* 상세보기 버튼 */}
                                        <button 
                                            onClick={(e) => handleViewClick(e, bookmark)}
                                            className="text-blue-600 hover:text-blue-800 p-1"
                                            title="상세보기"
                                        >
                                            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                        </button>
                                        {/* 수정 버튼 */}
                                        <button 
                                            onClick={(e) => handleEditClick(e, bookmark)}
                                            className="text-green-600 hover:text-green-800 p-1"
                                            title="수정"
                                        >
                                            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </button>
                                        {/* 삭제 버튼 */}
                                        <button 
                                            onClick={(e) => handleDeleteClick(e, bookmark)}
                                            className="text-red-600 hover:text-red-800 p-1"
                                            title="삭제"
                                        >
                                            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* 페이지네이션 */}
                    <div className="mt-4 overflow-x-auto">
                        {totalPages > 1 && (
                            <div className="flex justify-center">
                                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[8px] sm:text-[10px]">
                                    {/* 이전 페이지 버튼 */}
                                    <button
                                        onClick={() => handlePageChange(currentPage - 1)}
                                        disabled={currentPage === 1}
                                        className={`relative inline-flex items-center px-1.5 sm:px-2 py-1.5 sm:py-2 rounded-l-md border text-[8px] sm:text-[10px] font-medium ${
                                            currentPage === 1
                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                : 'bg-white text-gray-500 hover:bg-gray-50'
                                        }`}
                                    >
                                        이전
                                    </button>

                                    {/* 페이지 번호 */}
                                    {[...Array(totalPages)].map((_, i) => (
                                        <button
                                            key={i + 1}
                                            onClick={() => handlePageChange(i + 1)}
                                            className={`relative inline-flex items-center px-2 sm:px-4 py-1.5 sm:py-2 border text-[8px] sm:text-[10px] font-medium ${
                                                currentPage === i + 1
                                                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                            }`}
                                        >
                                            {i + 1}
                                        </button>
                                    ))}

                                    {/* 다음 페이지 버튼 */}
                                    <button
                                        onClick={() => handlePageChange(currentPage + 1)}
                                        disabled={currentPage === totalPages}
                                        className={`relative inline-flex items-center px-1.5 sm:px-2 py-1.5 sm:py-2 rounded-r-md border text-[8px] sm:text-[10px] font-medium ${
                                            currentPage === totalPages
                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                : 'bg-white text-gray-500 hover:bg-gray-50'
                                        }`}
                                    >
                                        다음
                                    </button>
                                </nav>
                            </div>
                        )}
                    </div>
                </>
            )}

            {showAddModal && (
                <AddBookmark
                    onClose={() => setShowAddModal(false)}
                    onAdd={handleAdd}
                    onDuplicateError={(message) => {
                        setShowAddModal(false);
                        setDuplicateErrorMessage(message);
                        setShowDuplicateErrorModal(true);
                    }}
                />
            )}
            {/* 중복 오류 UI: 북마크 추가 UI와 동일한 위치에 표시 */}
            {showDuplicateErrorModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center p-4 pt-8 sm:pt-12 lg:pt-16 z-50 overflow-y-auto">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] flex flex-col mt-4 sm:mt-8">
                        <div className="flex-none px-6 py-4 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-semibold text-gray-800">오류</h2>
                                <button
                                    type="button"
                                    onClick={() => setShowDuplicateErrorModal(false)}
                                    className="text-gray-500 hover:text-gray-700"
                                >
                                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeJoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-6">
                            <div className="flex items-start">
                                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                                    <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <p className="ml-3 text-gray-700">{duplicateErrorMessage}</p>
                            </div>
                        </div>
                        <div className="flex-none px-6 py-4 border-t border-gray-200 flex justify-end">
                            <button
                                type="button"
                                onClick={() => setShowDuplicateErrorModal(false)}
                                className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700"
                            >
                                확인
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {showEdit && selectedBookmark && (
                <EditBookmark
                    bookmark={selectedBookmark}
                    onClose={() => {
                        setShowEdit(false);
                        setSelectedBookmark(null);
                    }}
                    onUpdate={handleUpdate}
                />
            )}
            {showDelete && selectedBookmark && (
                <DeleteBookmark
                    bookmark={selectedBookmark}
                    onClose={() => {
                        setShowDelete(false);
                        setSelectedBookmark(null);
                    }}
                    onDelete={handleDelete}
                />
            )}
            </div>
        </div>
    );
};

export default BookmarkList; 