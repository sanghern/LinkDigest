export interface Bookmark {
    id: string;
    title: string;
    url: string;
    content: string;
    summary: string;
    source_name: string;
    created_at: string;
    updated_at: string;
    user_id: string;
    is_deleted: boolean;
    tags: string[];
    read_count: number;
} 