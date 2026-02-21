import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import Main from './components/Main';
import Login from './components/Login';
import BookmarkList from './components/BookmarkList';
import AddBookmark from './components/AddBookmark';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import LogViewer from './components/LogViewer';

function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <Router>
                    <div className="min-h-screen bg-gray-100">
                        <Navigation />
                        <Routes>
                            <Route path="/main" element={<Main />} />
                            <Route path="/login" element={<Login />} />
                            <Route
                                path="/bookmarks"
                                element={
                                    <ProtectedRoute>
                                        <BookmarkList />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/"
                                element={
                                    <ProtectedRoute>
                                        <BookmarkList />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="/add-bookmark" element={
                                <ProtectedRoute>
                                    <AddBookmark />
                                </ProtectedRoute>
                            } />
                            <Route path="/logs" element={
                                <ProtectedRoute>
                                    <LogViewer />
                                </ProtectedRoute>
                            } />
                            {/* 알 수 없는 경로는 첫 화면(main)으로 */}
                            <Route path="*" element={<Navigate to="/main" replace />} />
                        </Routes>
                    </div>
                </Router>
            </AuthProvider>
        </ErrorBoundary>
    );
}

export default App; 