import { useEffect, useMemo, useState } from 'react';
import { ChatCircleDots, PaperPlaneRight } from '@phosphor-icons/react';
import { api, getToken, setToken } from './api/client';
import AuthPanel from './components/AuthPanel';

const blockTypes = [
  { value: 'paragraph', label: 'Text' },
  { value: 'heading', label: 'Heading' },
  { value: 'list', label: 'List' },
  { value: 'quote', label: 'Quote' },
  { value: 'code', label: 'Code' }
];

const menuItems = [
  { id: 'notes', label: 'Notes' },
  { id: 'ai', label: 'AI Tools' },
  { id: 'chat', label: 'Chat AI' },
  { id: 'flashcards', label: 'Flashcards' },
  { id: 'dashboard', label: 'Dashboard' }
];

const gradeButtons = [
  { grade: 0, label: 'Again' },
  { grade: 1, label: 'Hard' },
  { grade: 2, label: 'Good' },
  { grade: 3, label: 'Easy' }
];

function blankBlock() {
  return { id: null, type: 'paragraph', content: '' };
}

function contentPreview(blocks) {
  return blocks.map((block) => block.content).filter(Boolean).join('\n').slice(0, 280);
}

export default function App() {
  const [user, setUser] = useState(null);
  const [workspace, setWorkspace] = useState(null);
  const [pages, setPages] = useState([]);
  const [decks, setDecks] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeView, setActiveView] = useState('notes');
  const [activePage, setActivePage] = useState(null);
  const [title, setTitle] = useState('');
  const [blocks, setBlocks] = useState([blankBlock()]);
  const [activeDeckId, setActiveDeckId] = useState(null);
  const [dueCards, setDueCards] = useState([]);
  const [generatedCards, setGeneratedCards] = useState([]);
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminIPs, setAdminIPs] = useState([]);
  const [adminStats, setAdminStats] = useState(null);
  const [adminIpForm, setAdminIpForm] = useState({ ip_address: '', reason: '' });
  const [adminLoading, setAdminLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatQuota, setChatQuota] = useState({ used: 0, remaining: 8, limit: 8 });
  const [chatLoading, setChatLoading] = useState(false);
  const [chatLoaded, setChatLoaded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aiLoading, setAiLoading] = useState('');
  const [reviewRevealed, setReviewRevealed] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  const activeDeck = useMemo(
    () => decks.find((deck) => deck.id === Number(activeDeckId)) || decks[0],
    [activeDeckId, decks]
  );
  const dueCard = dueCards[0];
  const visibleMenuItems = useMemo(
    () => (user?.is_admin ? [...menuItems, { id: 'admin', label: 'Admin' }] : menuItems),
    [user]
  );

  async function loadApp() {
    setError('');
    setLoading(true);
    try {
      const [me, boot] = await Promise.all([api.me(), api.bootstrap()]);
      setUser(me);
      setWorkspace(boot.workspace);
      setPages(boot.pages);
      setDecks(boot.decks);
      setStats(boot.stats);
      const deckId = boot.decks[0]?.id || null;
      setActiveDeckId(deckId);
      if (boot.pages[0]) {
        await loadPage(boot.pages[0].id);
      }
      if (deckId) {
        setDueCards(await api.deckCards(deckId, true));
      }
    } catch (err) {
      setError(err.message);
      if (err.message.includes('validate credentials')) {
        setToken(null);
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }

  async function refreshWorkspace(deckId = activeDeck?.id) {
    const boot = await api.bootstrap();
    setWorkspace(boot.workspace);
    setPages(boot.pages);
    setDecks(boot.decks);
    setStats(boot.stats);
    if (deckId) {
      setDueCards(await api.deckCards(deckId, true));
    }
  }

  async function loadPage(pageId) {
    const page = await api.page(pageId);
    setActivePage(page);
    setTitle(page.title);
    setBlocks(page.blocks?.length ? page.blocks.map(({ id, type, content }) => ({ id, type, content })) : [blankBlock()]);
    setGeneratedCards([]);
    setReviewRevealed(false);
  }

  useEffect(() => {
    if (getToken()) {
      loadApp();
    } else {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!search.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        setSearchResults(await api.search(search.trim()));
      } catch (err) {
        setError(err.message);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    if (activeView === 'admin' && user?.is_admin && adminUsers.length === 0 && adminIPs.length === 0) {
      loadAdmin();
    }
  }, [activeView, user?.is_admin]);

  useEffect(() => {
    if (activeView === 'chat' && !chatLoaded) {
      loadChat();
    }
  }, [activeView, chatLoaded]);

  async function createPage() {
    if (!workspace) return;
    const page = await api.createPage({ workspace_id: workspace.id, title: 'Untitled note', icon: 'note' });
    await refreshWorkspace();
    await loadPage(page.id);
    setActiveView('notes');
  }

  async function savePage() {
    if (!activePage) return null;
    setSaving(true);
    setNotice('');
    setError('');
    try {
      await api.updatePage(activePage.id, { title });
      const saved = await api.saveBlocks(
        activePage.id,
        blocks.map((block) => ({ id: block.id, type: block.type, content: block.content }))
      );
      setActivePage(saved);
      setBlocks(saved.blocks.map(({ id, type, content }) => ({ id, type, content })));
      await refreshWorkspace();
      setNotice('Đã lưu note.');
      return saved;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setSaving(false);
    }
  }

  async function deleteActivePage() {
    if (!activePage || pages.length <= 1) return;
    await api.deletePage(activePage.id);
    const remaining = pages.filter((page) => page.id !== activePage.id);
    await refreshWorkspace();
    if (remaining[0]) await loadPage(remaining[0].id);
  }

  function updateBlock(index, key, value) {
    setBlocks((current) => current.map((block, itemIndex) => (itemIndex === index ? { ...block, [key]: value } : block)));
  }

  function removeBlock(index) {
    setBlocks((current) => (current.length === 1 ? current : current.filter((_, itemIndex) => itemIndex !== index)));
  }

  async function summarize() {
    if (!activePage) return;
    const saved = await savePage();
    if (!saved) return;
    setActiveView('ai');
    setAiLoading('summary');
    setError('');
    try {
      const result = await api.summarizePage(activePage.id);
      setActivePage((page) => ({ ...page, summary: result.summary }));
      setNotice('AI đã tóm tắt note.');
    } catch (err) {
      setError(err.message);
    } finally {
      setAiLoading('');
    }
  }

  async function generateCards() {
    if (!activePage) return;
    const saved = await savePage();
    if (!saved) return;
    setActiveView('ai');
    setAiLoading('cards');
    setError('');
    try {
      const result = await api.generateCards(activePage.id);
      setGeneratedCards(result.cards);
      setNotice(`AI tạo ${result.cards.length} flashcards.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setAiLoading('');
    }
  }

  async function acceptGeneratedCards() {
    if (!activeDeck || !activePage) return;
    await Promise.all(
      generatedCards.map((card) =>
        api.createCard({
          deck_id: activeDeck.id,
          page_id: activePage.id,
          front: card.front,
          back: card.back,
          source_text: card.source_text
        })
      )
    );
    setGeneratedCards([]);
    await refreshWorkspace(activeDeck.id);
    setDueCards(await api.deckCards(activeDeck.id, true));
    setActiveView('flashcards');
    setNotice('Đã thêm flashcards vào deck.');
  }

  async function review(grade) {
    if (!dueCard || !activeDeck) return;
    await api.reviewCard({ card_id: dueCard.id, grade });
    setReviewRevealed(false);
    await refreshWorkspace(activeDeck.id);
    setDueCards(await api.deckCards(activeDeck.id, true));
  }

  async function loadAdmin() {
    if (!user?.is_admin) return;
    setAdminLoading(true);
    setError('');
    try {
      const [stats, users, ips] = await Promise.all([api.adminStats(), api.adminUsers(), api.adminIPAddresses()]);
      setAdminStats(stats);
      setAdminUsers(users);
      setAdminIPs(ips);
    } catch (err) {
      setError(err.message);
    } finally {
      setAdminLoading(false);
    }
  }

  async function loadChat() {
    setError('');
    try {
      const history = await api.chatHistory();
      setChatMessages(history.messages || []);
      setChatQuota({ used: history.used, remaining: history.remaining, limit: history.limit });
      setChatLoaded(true);
    } catch (err) {
      setError(err.message);
    }
  }

  async function sendChat(event) {
    event.preventDefault();
    const question = chatQuestion.trim();
    if (!question || chatLoading || chatQuota.remaining <= 0) return;

    setChatLoading(true);
    setError('');
    try {
      const result = await api.askChat({ question });
      setChatMessages((current) => [...current, result.message]);
      setChatQuota({ used: result.used, remaining: result.remaining, limit: result.limit });
      setChatQuestion('');
    } catch (err) {
      setError(err.message);
      await loadChat();
    } finally {
      setChatLoading(false);
    }
  }

  async function toggleUserLock(targetUser) {
    setError('');
    try {
      if (targetUser.is_locked) {
        await api.unlockUser(targetUser.id);
        setNotice(`Đã mở khóa ${targetUser.username}.`);
      } else {
        await api.lockUser(targetUser.id);
        setNotice(`Đã khóa ${targetUser.username}.`);
      }
      await loadAdmin();
    } catch (err) {
      setError(err.message);
    }
  }

  async function blockIP(ipAddress, reason = '') {
    const targetIP = ipAddress.trim();
    if (!targetIP) return;
    setError('');
    try {
      await api.blockIP({ ip_address: targetIP, reason: reason.trim() || null });
      setAdminIpForm({ ip_address: '', reason: '' });
      setNotice(`Đã chặn IP ${targetIP}.`);
      await loadAdmin();
    } catch (err) {
      setError(err.message);
    }
  }

  async function unblockIP(ipAddress) {
    setError('');
    try {
      await api.unblockIP(ipAddress);
      setNotice(`Đã bỏ chặn IP ${ipAddress}.`);
      await loadAdmin();
    } catch (err) {
      setError(err.message);
    }
  }

  function logout() {
    setToken(null);
    setUser(null);
    setWorkspace(null);
    setPages([]);
    setDecks([]);
    setStats(null);
    setActivePage(null);
    setAdminUsers([]);
    setAdminIPs([]);
    setAdminStats(null);
    setChatMessages([]);
    setChatQuestion('');
    setChatQuota({ used: 0, remaining: 8, limit: 8 });
    setChatLoaded(false);
    setActiveView('notes');
  }

  if (loading) {
    return <div className="loading-screen">Loading MindDeckNote Lite...</div>;
  }

  if (!user) {
    return <AuthPanel onAuthenticated={loadApp} />;
  }

  return (
    <div className="mind-app">
      <header className="app-header">
        <div className="app-brand">
          <div className="brand-mark">MD</div>
          <div>
            <strong>MindDeckNote</strong>
            <span>{workspace?.name || 'Workspace'}</span>
          </div>
        </div>

        <nav className="top-menu" aria-label="Main menu">
          {visibleMenuItems.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? 'active' : ''}
              onClick={() => setActiveView(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="header-actions">
          {user.is_admin && (
            <button
              className={activeView === 'admin' ? 'admin-shortcut active' : 'admin-shortcut'}
              onClick={() => setActiveView('admin')}
              type="button"
            >
              Admin
            </button>
          )}
          <span className="user-chip">
            {user.username}
            {user.is_admin && <small>Admin</small>}
          </span>
          <button className="ghost-button small" onClick={logout}>Logout</button>
        </div>
      </header>

      <main className="app-main">
        {(notice || error) && (
          <div className={error ? 'notice error' : 'notice'}>{error || notice}</div>
        )}

        {activeView === 'notes' && (
          <section className="workspace-grid">
            <aside className="panel note-browser">
              <div className="panel-heading">
                <div>
                  <h2>Notes</h2>
                  <p>{pages.length} pages trong workspace</p>
                </div>
                <button className="primary-action small" onClick={createPage}>New note</button>
              </div>

              <label className="field-label" htmlFor="note-search">Search</label>
              <input
                id="note-search"
                className="field-input compact"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Tìm note hoặc nội dung"
              />

              {searchResults.length > 0 && (
                <div className="search-results">
                  {searchResults.map((result) => (
                    <button
                      key={result.page.id}
                      onClick={async () => {
                        await loadPage(result.page.id);
                        setSearch('');
                      }}
                    >
                      <strong>{result.page.title}</strong>
                      <span>{result.snippet || 'Không có preview'}</span>
                    </button>
                  ))}
                </div>
              )}

              <div className="page-list">
                {pages.map((page) => (
                  <button
                    key={page.id}
                    className={activePage?.id === page.id ? 'active' : ''}
                    onClick={() => loadPage(page.id)}
                  >
                    <span>{page.title}</span>
                    <small>{new Date(page.updated_at).toLocaleDateString('vi-VN')}</small>
                  </button>
                ))}
              </div>
            </aside>

            <section className="panel editor-panel">
              <header className="editor-header">
                <div>
                  <span className="section-kicker">Block editor</span>
                  <input
                    className="title-input"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    placeholder="Untitled note"
                  />
                </div>
                <div className="editor-actions">
                  <button className="ghost-button danger" onClick={deleteActivePage} disabled={pages.length <= 1}>Delete</button>
                  <button className="ghost-button" onClick={() => setBlocks([...blocks, blankBlock()])}>Add block</button>
                  <button className="primary-action" onClick={savePage} disabled={saving}>
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </header>

              <div className="block-editor">
                {blocks.map((block, index) => (
                  <article className={`note-block ${block.type}`} key={`${block.id || 'new'}-${index}`}>
                    <select value={block.type} onChange={(event) => updateBlock(index, 'type', event.target.value)}>
                      {blockTypes.map((type) => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                    <textarea
                      value={block.content}
                      onChange={(event) => updateBlock(index, 'content', event.target.value)}
                      placeholder={block.type === 'heading' ? 'Heading' : 'Write something useful'}
                      rows={block.type === 'heading' ? 2 : 4}
                    />
                    <button className="remove-block" onClick={() => removeBlock(index)} aria-label="Remove block">x</button>
                  </article>
                ))}
              </div>
            </section>
          </section>
        )}

        {activeView === 'ai' && (
          <section className="two-column-view">
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>AI Tools</h2>
                  <p>Dùng note hiện tại để tóm tắt hoặc sinh flashcards.</p>
                </div>
              </div>

              <div className="note-preview">
                <span>Current note</span>
                <strong>{title || 'Untitled note'}</strong>
                <p>{contentPreview(blocks) || 'Chưa có nội dung để AI xử lý.'}</p>
              </div>

              <div className="action-row">
                <button className="primary-action" onClick={summarize} disabled={aiLoading}>
                  {aiLoading === 'summary' ? 'Summarizing...' : 'Summarize note'}
                </button>
                <button className="ghost-button" onClick={generateCards} disabled={aiLoading}>
                  {aiLoading === 'cards' ? 'Generating...' : 'Generate cards'}
                </button>
              </div>

              {activePage?.summary && (
                <div className="ai-summary">
                  <strong>Summary</strong>
                  <p>{activePage.summary}</p>
                </div>
              )}
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Draft flashcards</h2>
                  <p>Kiểm tra nhanh trước khi thêm vào deck.</p>
                </div>
                {generatedCards.length > 0 && (
                  <button className="primary-action small" onClick={acceptGeneratedCards}>Add all</button>
                )}
              </div>

              {generatedCards.length === 0 ? (
                <div className="empty-state">Chưa có draft card. Bấm Generate cards để tạo từ note.</div>
              ) : (
                <div className="draft-list roomy">
                  {generatedCards.map((card, index) => (
                    <article key={`${card.front}-${index}`}>
                      <strong>{card.front}</strong>
                      <span>{card.back}</span>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </section>
        )}

        {activeView === 'chat' && (
          <section className="chat-view">
            <aside className="panel chat-side">
              <div className="chat-identity">
                <div className="chat-icon" aria-hidden="true">
                  <ChatCircleDots size={30} weight="duotone" />
                </div>
                <div>
                  <span className="section-kicker">Rule based assistant</span>
                  <h2>Hỏi nhanh về cloud và note</h2>
                  <p>Câu quen thuộc sẽ trả lời bằng rule. Câu còn lại sẽ chuyển sang AI provider.</p>
                </div>
              </div>

              <div className="quota-card">
                <div>
                  <span>Lượt còn lại</span>
                  <strong>{chatQuota.remaining}/{chatQuota.limit}</strong>
                </div>
                <div className="quota-meter" aria-hidden="true">
                  <span style={{ width: `${chatQuota.limit ? (chatQuota.used / chatQuota.limit) * 100 : 0}%` }} />
                </div>
                <p>Mỗi tài khoản được hỏi tối đa {chatQuota.limit} lần. Lượt chỉ tính khi hệ thống đã trả lời thành công.</p>
              </div>
            </aside>

            <section className="panel chat-panel">
              <div className="chat-panel-header">
                <div>
                  <h2>Chat AI</h2>
                  <p>{chatMessages.length} câu đã hỏi trong tài khoản này</p>
                </div>
                <button className="ghost-button small" onClick={loadChat} disabled={chatLoading}>Refresh</button>
              </div>

              <div className="chat-messages">
                {chatMessages.length === 0 ? (
                  <div className="empty-state chat-empty">Thử hỏi: Hệ thống này đủ IaaS đến SaaS chưa?</div>
                ) : (
                  chatMessages.map((message) => (
                    <article className="chat-turn" key={message.id}>
                      <div className="chat-question">
                        <span>Bạn</span>
                        <p>{message.question}</p>
                      </div>
                      <div className="chat-answer">
                        <div className="assistant-line">
                          <span className="assistant-avatar" aria-hidden="true">
                            <ChatCircleDots size={18} weight="duotone" />
                          </span>
                          <strong>MindDeck AI</strong>
                          <mark className="source-pill">{message.source === 'rule' ? 'Rule based' : 'AI provider'}</mark>
                        </div>
                        <p>{message.answer}</p>
                        <small>{new Date(message.created_at).toLocaleString('vi-VN')}</small>
                      </div>
                    </article>
                  ))
                )}
              </div>

              <form className="chat-form" onSubmit={sendChat}>
                <textarea
                  className="field-input chat-input"
                  value={chatQuestion}
                  onChange={(event) => setChatQuestion(event.target.value)}
                  placeholder={chatQuota.remaining <= 0 ? 'Tài khoản đã hết lượt hỏi AI' : 'Nhập câu hỏi của bạn'}
                  rows={2}
                  disabled={chatLoading || chatQuota.remaining <= 0}
                />
                <button className="primary-action send-button" disabled={chatLoading || chatQuota.remaining <= 0 || !chatQuestion.trim()}>
                  <PaperPlaneRight size={18} weight="bold" />
                  <span>{chatLoading ? 'Đang hỏi...' : 'Gửi'}</span>
                </button>
              </form>
            </section>
          </section>
        )}

        {activeView === 'flashcards' && (
          <section className="two-column-view">
            <section className="panel review-panel">
              <div className="panel-heading">
                <div>
                  <h2>Review</h2>
                  <p>{stats?.due_cards || 0} cards đến hạn hôm nay</p>
                </div>
                <select
                  className="field-input compact deck-select"
                  value={activeDeck?.id || ''}
                  onChange={async (event) => {
                    const deckId = Number(event.target.value);
                    setActiveDeckId(deckId);
                    setDueCards(await api.deckCards(deckId, true));
                  }}
                >
                  {decks.map((deck) => (
                    <option key={deck.id} value={deck.id}>{deck.name}</option>
                  ))}
                </select>
              </div>

              {!dueCard ? (
                <div className="empty-state">Không còn card đến hạn. Tạo thêm flashcard từ AI Tools để demo tiếp.</div>
              ) : (
                <>
                  <div className="flashcard large">
                    <span>Front</span>
                    <strong>{dueCard.front}</strong>
                    {reviewRevealed && <p>{dueCard.back}</p>}
                  </div>
                  {!reviewRevealed ? (
                    <button className="primary-action w-100" onClick={() => setReviewRevealed(true)}>Reveal answer</button>
                  ) : (
                    <div className="grade-grid">
                      {gradeButtons.map((button) => (
                        <button key={button.grade} onClick={() => review(button.grade)}>{button.label}</button>
                      ))}
                    </div>
                  )}
                </>
              )}
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Deck status</h2>
                  <p>{activeDeck?.name || 'Default deck'}</p>
                </div>
              </div>
              <div className="stat-grid wide">
                <div><strong>{stats?.cards || 0}</strong><span>Total cards</span></div>
                <div><strong>{stats?.due_cards || 0}</strong><span>Due cards</span></div>
                <div><strong>{stats?.studied_today || 0}</strong><span>Studied today</span></div>
                <div><strong>{stats?.decks || 0}</strong><span>Decks</span></div>
              </div>
            </section>
          </section>
        )}

        {activeView === 'dashboard' && (
          <section className="dashboard-view">
            <div className="panel hero-panel">
              <span className="section-kicker">Project overview</span>
              <h1>MindDeckNote Lite đang chạy trên EC2.</h1>
              <p>Demo đủ lớp cloud: Nginx, React, FastAPI, PostgreSQL, Docker network và external AI API.</p>
            </div>

            <div className="stat-grid dashboard-stats">
              <div><strong>{stats?.pages || 0}</strong><span>Notes</span></div>
              <div><strong>{stats?.blocks || 0}</strong><span>Blocks</span></div>
              <div><strong>{stats?.cards || 0}</strong><span>Cards</span></div>
              <div><strong>{stats?.studied_today || 0}</strong><span>Studied today</span></div>
            </div>

            <div className="panel architecture-panel">
              <h2>Architecture</h2>
              <div className="architecture-row">
                <span>Browser</span>
                <span>Nginx</span>
                <span>React</span>
                <span>FastAPI</span>
                <span>PostgreSQL</span>
                <span>Mimo API</span>
              </div>
            </div>
          </section>
        )}

        {activeView === 'admin' && user?.is_admin && (
          <section className="admin-view">
            <section className="panel admin-hero">
              <div>
                <span className="section-kicker">Admin access</span>
                <h1>Quản lý tài khoản và IP truy cập</h1>
                <p>Khóa tài khoản vi phạm hoặc chặn IP ở tầng ứng dụng. Các thao tác có hiệu lực ngay trên API.</p>
              </div>
              <button className="primary-action" onClick={loadAdmin} disabled={adminLoading}>
                {adminLoading ? 'Đang tải...' : 'Refresh'}
              </button>
            </section>

            <section className="admin-stat-grid">
              <div>
                <strong>{adminStats?.active_users || 0}</strong>
                <span>User đang truy cập</span>
                <small>{adminStats?.window_minutes || 5} phút gần nhất</small>
              </div>
              <div>
                <strong>{adminStats?.active_ips || 0}</strong>
                <span>IP đang hoạt động</span>
                <small>Theo request API</small>
              </div>
              <div>
                <strong>{adminStats?.total_users || adminUsers.length}</strong>
                <span>Tổng tài khoản</span>
                <small>{adminStats?.locked_users || 0} tài khoản bị khóa</small>
              </div>
              <div>
                <strong>{adminStats?.blocked_ips || 0}</strong>
                <span>IP bị chặn</span>
                <small>Blocklist ứng dụng</small>
              </div>
            </section>

            <section className="admin-grid">
              <section className="panel admin-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Tài khoản</h2>
                    <p>{adminUsers.length} người dùng trong hệ thống</p>
                  </div>
                </div>

                <div className="admin-table">
                  <div className="admin-table-row admin-table-head">
                    <span>User</span>
                    <span>Quyền</span>
                    <span>Trạng thái</span>
                    <span>IP gần nhất</span>
                    <span>Thao tác</span>
                  </div>
                  {adminUsers.map((targetUser) => {
                    const lastIP = targetUser.ip_addresses?.[0];
                    return (
                      <div className="admin-table-row" key={targetUser.id}>
                        <span>
                          <strong>{targetUser.username}</strong>
                          <small>{targetUser.email}</small>
                        </span>
                        <span>{targetUser.is_admin ? 'Admin' : 'User'}</span>
                        <span>
                          <mark className={targetUser.is_locked ? 'status-pill locked' : 'status-pill'}>
                            {targetUser.is_locked ? 'Locked' : 'Active'}
                          </mark>
                        </span>
                        <span>
                          <code>{lastIP?.ip_address || 'Chưa có'}</code>
                          {lastIP?.is_blocked && <small className="danger-text">IP bị chặn</small>}
                        </span>
                        <span>
                          <button
                            className={targetUser.is_locked ? 'ghost-button small' : 'ghost-button small danger'}
                            onClick={() => toggleUserLock(targetUser)}
                            disabled={targetUser.id === user.id}
                          >
                            {targetUser.is_locked ? 'Mở khóa' : 'Khóa'}
                          </button>
                        </span>
                      </div>
                    );
                  })}
                </div>
              </section>

              <section className="panel admin-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Địa chỉ IP</h2>
                    <p>Theo dõi IP đã đăng nhập và IP đang bị block.</p>
                  </div>
                </div>

                <form
                  className="ip-block-form"
                  onSubmit={(event) => {
                    event.preventDefault();
                    blockIP(adminIpForm.ip_address, adminIpForm.reason);
                  }}
                >
                  <input
                    className="field-input compact"
                    value={adminIpForm.ip_address}
                    onChange={(event) => setAdminIpForm({ ...adminIpForm, ip_address: event.target.value })}
                    placeholder="VD: 113.161.10.25"
                  />
                  <input
                    className="field-input compact"
                    value={adminIpForm.reason}
                    onChange={(event) => setAdminIpForm({ ...adminIpForm, reason: event.target.value })}
                    placeholder="Lý do chặn"
                  />
                  <button className="primary-action small">Chặn IP</button>
                </form>

                <div className="admin-table ip-table">
                  <div className="admin-table-row admin-table-head">
                    <span>IP</span>
                    <span>User</span>
                    <span>Lượt</span>
                    <span>Gần nhất</span>
                    <span>Thao tác</span>
                  </div>
                  {adminIPs.map((ip) => (
                    <div className="admin-table-row" key={`${ip.ip_address}-${ip.user_id || 'blocked'}`}>
                      <span>
                        <code>{ip.ip_address}</code>
                        {ip.is_blocked && <small className="danger-text">{ip.block_reason || 'Blocked'}</small>}
                      </span>
                      <span>
                        <strong>{ip.username || 'Không gắn user'}</strong>
                        {ip.email && <small>{ip.email}</small>}
                      </span>
                      <span>{ip.request_count || 0}</span>
                      <span>{ip.last_seen_at ? new Date(ip.last_seen_at).toLocaleString('vi-VN') : 'Chưa có'}</span>
                      <span>
                        {ip.is_blocked ? (
                          <button className="ghost-button small" onClick={() => unblockIP(ip.ip_address)}>Bỏ chặn</button>
                        ) : (
                          <button className="ghost-button small danger" onClick={() => blockIP(ip.ip_address, 'Blocked from admin panel')}>
                            Chặn
                          </button>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            </section>
          </section>
        )}
      </main>
    </div>
  );
}
