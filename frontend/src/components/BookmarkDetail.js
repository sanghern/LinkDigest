import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { formatDate } from '../utils/dateUtils';
import api from '../utils/api';
import LoadingSpinner from './LoadingSpinner';

const BookmarkDetail = ({ bookmark, onClose, currentPage, totalPages, onPageChange }) => {
    // showContent의 초기값 설정을 안전하게 처리
    const [showContent, setShowContent] = useState(() => {
        if (!bookmark) return true;
        return !bookmark.summary || bookmark.summary === '요약 생성 중...';
    });
    
    const [currentBookmark, setCurrentBookmark] = useState(bookmark);
    const [isLoading, setIsLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const readCountIncreasedRef = useRef(null); // 현재 조회수 증가한 북마크 ID
    const isIncreasingRef = useRef(false); // 조회수 증가 중인지 추적 (중복 실행 방지)

    // bookmark prop이 변경될 때 currentBookmark 업데이트
    useEffect(() => {
        if (bookmark && bookmark.id !== currentBookmark?.id) {
            setCurrentBookmark(bookmark);
        }
    }, [bookmark, currentBookmark?.id]);

    // bookmark.id가 변경될 때만 조회수 증가 (컴포넌트 인스턴스당 한 번만, 중복 실행 방지)
    useEffect(() => {
        // bookmark.id가 있고, 이전에 증가시킨 ID와 다르고, 현재 증가 중이 아닌 경우에만 실행
        if (bookmark?.id && readCountIncreasedRef.current !== bookmark.id && !isIncreasingRef.current) {
            isIncreasingRef.current = true; // 증가 중 플래그 설정
            const increaseReadCount = async () => {
                try {
                    console.log(`조회수 증가 시작: ${bookmark.id}`);
                    await api.bookmarks.increaseReadCount(bookmark.id);
                    readCountIncreasedRef.current = bookmark.id; // 조회수 증가 완료 표시
                    console.log(`조회수 증가 완료: ${bookmark.id}`);
                } catch (error) {
                    console.error('조회수 증가 실패:', error);
                    // 에러 발생 시 플래그 리셋하여 재시도 가능하도록
                    isIncreasingRef.current = false;
                } finally {
                    // 성공/실패 관계없이 플래그 리셋 (단, 성공한 경우는 readCountIncreasedRef로 추적)
                    if (readCountIncreasedRef.current === bookmark.id) {
                        isIncreasingRef.current = false;
                    }
                }
            };
            increaseReadCount();
        }
    }, [bookmark?.id]); // bookmark.id만 의존성으로 사용

    // 요약 상태 확인 및 업데이트
    useEffect(() => {
        let intervalId;
        
        const checkSummary = async () => {
            if (!currentBookmark?.summary || currentBookmark.summary === '요약 생성 중...') {
                setIsLoading(true);
                try {
                    const response = await api.bookmarks.getBookmark(currentBookmark.id);
                    if (!response) {
                        console.error('북마크 정보를 가져올 수 없음');
                        return;
                    }
                    
                    setCurrentBookmark(response);
                    
                    // 요약이 완료되면 인터벌 중지 및 로딩 상태 해제
                    if (response.summary && response.summary !== '요약 생성 중...') {
                        clearInterval(intervalId);
                        setIsLoading(false);
                        setShowContent(false);  // 요약 보기로 전환
                    }
                } catch (error) {
                    console.error('요약 상태 확인 실패:', error);
                    // 에러 발생 시에도 인터벌은 유지하고 로딩 상태만 해제
                    setIsLoading(false);
                }
            }
        };

        // 북마크 ID가 있을 때만 인터벌 시작
        if (currentBookmark?.id) {
            checkSummary();  // 최초 1회 실행
            intervalId = setInterval(checkSummary, 2000);
        }
        
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [currentBookmark?.id, currentBookmark?.summary]);

    // 리스트로 돌아가기 핸들러
    const handleClose = () => {
        onClose();
    };

    // 페이지 변경 핸들러 - 페이지 변경 후 목록으로 돌아가기
    const handlePageChange = (page) => {
        onClose(false, page);  // 페이지 번호를 전달하여 상세보기를 닫고 해당 페이지로 이동
    };

    // 수정 버튼 클릭 핸들러
    const handleEditClick = (e) => {
        e.stopPropagation();
        onClose(true);  // true를 전달하여 수정 모달을 열도록 함
    };

    useEffect(() => {
        if (bookmark) {
            setIsInitialLoading(false);
        }
    }, [bookmark]);

    // Early return을 hooks 호출 이후로 이동
    if (!bookmark || !currentBookmark) {
        return null;
    }

    if (isInitialLoading) {
        return (
            <div className="bg-white rounded-lg shadow-xl w-full p-4 sm:p-6">
                <LoadingSpinner message="북마크 정보를 불러오는 중..." />
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-xl w-full flex flex-col">
            {/* 상단 섹션: 뒤로가기 버튼과 페이지네이션을 같은 라인에 배치 */}
            <div className="flex-none px-3 sm:px-6 lg:px-8 xl:px-10 py-3 sm:py-4 border-b border-gray-200">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 sm:mb-4 gap-3 sm:gap-0">
                    {/* 왼쪽: 리스트로 돌아가기 버튼 */}
                    <button 
                        onClick={handleClose} 
                        className="flex items-center justify-center w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                        title="리스트로 돌아가기"
                        aria-label="리스트로 돌아가기"
                    >
                        <svg className="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" strokeWidth="2.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                        </svg>
                    </button>

                    {/* 오른쪽: 페이지네이션 */}
                    {totalPages > 1 && (
                        <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px text-[8px] sm:text-[10px] w-full sm:w-auto overflow-x-auto">
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
                </div>

                {/* 제목 및 메타 정보 */}
                <div className="space-y-2">
                    <div className="flex justify-between items-start">
                        <h2 className="text-base sm:text-xl font-semibold text-gray-800 break-words pr-2">{currentBookmark.title}</h2>
                    </div>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0 text-xs sm:text-sm text-gray-500">
                        {/* 왼쪽: 메타 정보 */}
                        <div className="flex flex-wrap items-center gap-2 sm:gap-4">
                            <span>{formatDate(currentBookmark.created_at)}</span>
                            <span className="hidden sm:inline">·</span>
                            <span className="truncate max-w-[150px] sm:max-w-none">{currentBookmark.source_name || '-'}</span>
                        </div>
                        
                        {/* 오른쪽: 버튼들 */}
                        <div className="flex items-center space-x-1 sm:space-x-2 w-full sm:w-auto">
                            {/* 요약/컨텐츠 토글 버튼 */}
                            <div className="inline-flex rounded-lg shadow-sm flex-1 sm:flex-none">
                                <button 
                                    onClick={() => setShowContent(false)}
                                    className={`px-2 sm:px-3 py-1 text-[10px] sm:text-xs font-medium rounded-l-lg border flex-1 sm:flex-none
                                        ${!showContent 
                                            ? 'bg-blue-50 text-blue-600 border-blue-600' 
                                            : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                                    disabled={isLoading}
                                >
                                    <span className="hidden sm:inline">요약 {isLoading ? '(로딩중...)' : !currentBookmark.summary && '(클릭하여 확인)'}</span>
                                    <span className="sm:hidden">요약</span>
                                </button>
                                <button 
                                    onClick={() => setShowContent(true)}
                                    className={`px-2 sm:px-3 py-1 text-[10px] sm:text-xs font-medium rounded-r-lg border-t border-r border-b flex-1 sm:flex-none
                                        ${showContent 
                                            ? 'bg-blue-50 text-blue-600 border-blue-600' 
                                            : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    컨텐츠
                                </button>
                            </div>

                            {/* 구분선 */}
                            <div className="h-4 w-px bg-gray-300 mx-1 sm:mx-2 hidden sm:block"></div>

                            {/* 수정 버튼 */}
                            <button 
                                onClick={handleEditClick}
                                className="text-green-600 hover:text-green-800 p-1"
                                title="수정"
                            >
                                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    {bookmark.tags && bookmark.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 sm:gap-2">
                            {bookmark.tags.map((tag, index) => (
                                <span key={index} className="bg-blue-100 text-blue-800 px-1.5 sm:px-2 py-0.5 rounded text-xs sm:text-sm">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* 중앙 컨텐츠 영역 */}
            <div className="flex-1 overflow-y-auto min-h-0 p-3 sm:p-6 lg:p-8 xl:p-10">
                <div className="w-full prose prose-sm sm:prose-sm lg:prose xl:prose-lg prose-headings:font-semibold prose-p:leading-relaxed prose-table:w-full prose-table:table-auto prose-img:rounded-lg prose-img:shadow-md" style={{ maxWidth: 'none' }}>
                    <ReactMarkdown 
                        rehypePlugins={[rehypeRaw]} 
                        remarkPlugins={[remarkGfm]}
                        className="markdown-body text-xs sm:text-sm lg:text-base xl:text-lg w-full"
                        components={{
                            a: ({ node, ...props }) => (
                                <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 hover:underline">
                                    {props.children}
                                </a>
                            ),
                            // 코드 블록 커스텀 컴포넌트 - 다크 테마 적용
                            pre: ({ node, children, ...props }) => (
                                <pre 
                                    {...props} 
                                    className="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4 overflow-x-auto border border-gray-700 font-mono"
                                    style={{
                                        WebkitOverflowScrolling: 'touch',
                                        whiteSpace: 'pre'
                                    }}
                                >
                                    {children}
                                </pre>
                            ),
                            // 코드 요소 커스텀 컴포넌트
                            code: ({ node, inline, className, children, ...props }) => {
                                // 코드 블록 내부의 코드인지 확인
                                const isBlockCode = !inline;
                                if (isBlockCode) {
                                    return (
                                        <code 
                                            {...props} 
                                            className="bg-transparent text-gray-100 p-0 font-mono"
                                            style={{ whiteSpace: 'pre' }}
                                        >
                                            {children}
                                        </code>
                                    );
                                }
                                // 인라인 코드
                                return (
                                    <code 
                                        {...props} 
                                        className="bg-gray-100 text-gray-900 px-1 rounded font-mono"
                                    >
                                        {children}
                                    </code>
                                );
                            },
                        }}
                    >
                        {showContent 
                            ? (currentBookmark.content || '컨텐츠가 없습니다.') 
                            : (currentBookmark.summary || '요약이 생성중입니다...')}
                    </ReactMarkdown>
                </div>
            </div>

            {/* 하단 섹션 */}
            <div className="flex-none px-3 sm:px-6 lg:px-8 xl:px-10 py-3 sm:py-4 border-t border-gray-200">
                <div className="space-y-2">
                    {/* 첫 번째 줄: 목록으로 돌아가기 아이콘, 출처, URL */}
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-500">
                        {/* 목록으로 돌아가기 아이콘 */}
                        <button 
                            onClick={handleClose} 
                            className="flex items-center justify-center w-5 h-5 sm:w-6 sm:h-6 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                            title="리스트로 돌아가기"
                            aria-label="리스트로 돌아가기"
                        >
                            <svg className="w-2.5 h-2.5 sm:w-3 sm:h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" strokeWidth="2.5">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                            </svg>
                        </button>
                        <span className="hidden sm:inline text-gray-300">|</span>
                        <div className="flex items-center">
                            <span className="font-medium mr-1 sm:mr-2">출처:</span>
                            <span className="truncate max-w-[200px] sm:max-w-none">{currentBookmark.source_name || '-'}</span>
                        </div>
                        <span className="hidden sm:inline text-gray-300">|</span>
                        <div className="flex items-start sm:items-center overflow-hidden w-full sm:w-auto">
                            <span className="font-medium mr-1 sm:mr-2 flex-shrink-0">URL:</span>
                            <a 
                                href={currentBookmark.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="truncate text-blue-600 hover:text-blue-800 hover:underline break-all sm:break-normal"
                            >
                                {currentBookmark.url}
                            </a>
                        </div>
                    </div>

                    {/* 두 번째 줄: 생성일, 수정일, 조회수 */}
                    <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-500">
                        <div className="flex items-center">
                            <span className="font-medium mr-1 sm:mr-2">생성일:</span>
                            <span>{formatDate(currentBookmark.created_at)}</span>
                        </div>
                        <span className="hidden sm:inline text-gray-300">|</span>
                        <div className="flex items-center">
                            <span className="font-medium mr-1 sm:mr-2">수정일:</span>
                            <span>{currentBookmark.updated_at ? formatDate(currentBookmark.updated_at) : '-'}</span>
                        </div>
                        <span className="hidden sm:inline text-gray-300">|</span>
                        <div className="flex items-center">
                            <span className="font-medium mr-1 sm:mr-2">조회수:</span>
                            <span>{currentBookmark.read_count || 0}회</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BookmarkDetail; 