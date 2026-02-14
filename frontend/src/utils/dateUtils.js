import { format } from 'date-fns';

export const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
        return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss');
    } catch (error) {
        console.error('날짜 형식 변환 오류:', error);
        return dateString;
    }
}; 