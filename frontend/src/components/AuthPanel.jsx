import { useState } from 'react';
import { api, setToken } from '../api/client';

export default function AuthPanel({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [loginForm, setLoginForm] = useState({ identifier: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const currentForm = mode === 'login' ? loginForm : registerForm;

  function updateLogin(event) {
    setLoginForm({ ...loginForm, [event.target.name]: event.target.value });
  }

  function updateRegister(event) {
    setRegisterForm({ ...registerForm, [event.target.name]: event.target.value });
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setError('');
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'register') {
        await api.register({
          username: registerForm.username.trim(),
          email: registerForm.email.trim(),
          password: registerForm.password
        });
        const token = await api.login(registerForm.username.trim(), registerForm.password);
        setToken(token.access_token);
      } else {
        const token = await api.login(loginForm.identifier.trim(), loginForm.password);
        setToken(token.access_token);
      }
      await onAuthenticated();
    } catch (err) {
      setError(err.message || 'Không thể đăng nhập. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <header className="auth-topbar">
        <div className="brand-mark">MD</div>
        <div>
          <strong>MindDeckNote Lite</strong>
          <span>Notes, AI summary, flashcards</span>
        </div>
      </header>

      <section className="auth-layout">
        <div className="auth-intro">
          <p className="eyebrow">Cloud Computing Mini Project</p>
          <h1>Ghi chú nhanh, học lại thông minh.</h1>
          <p className="lead">
            Một workspace đơn giản để demo React, FastAPI, PostgreSQL, Docker, Nginx và Mimo AI API.
          </p>
          <div className="architecture-strip" aria-label="MindDeckNote architecture">
            <span>React</span>
            <span>Nginx</span>
            <span>FastAPI</span>
            <span>PostgreSQL</span>
            <span>Mimo API</span>
          </div>
        </div>

        <section className="auth-card">
          <div className="auth-card-heading">
            <span>Workspace access</span>
            <h2>{mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}</h2>
          </div>

          <div className="segmented" role="group" aria-label="Authentication mode">
            <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => switchMode('login')}>
              Login
            </button>
            <button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => switchMode('register')}>
              Register
            </button>
          </div>

          <form className="auth-form" onSubmit={submit}>
            {mode === 'login' ? (
              <>
                <label className="field-label" htmlFor="login-identifier">Username hoặc email</label>
                <input
                  id="login-identifier"
                  className="field-input"
                  name="identifier"
                  value={loginForm.identifier}
                  onChange={updateLogin}
                  autoComplete="username"
                  required
                />
              </>
            ) : (
              <>
                <label className="field-label" htmlFor="register-username">Username</label>
                <input
                  id="register-username"
                  className="field-input"
                  name="username"
                  minLength={3}
                  value={registerForm.username}
                  onChange={updateRegister}
                  autoComplete="username"
                  required
                />

                <label className="field-label" htmlFor="register-email">Email</label>
                <input
                  id="register-email"
                  className="field-input"
                  type="email"
                  name="email"
                  value={registerForm.email}
                  onChange={updateRegister}
                  autoComplete="email"
                  required
                />
              </>
            )}

            <label className="field-label" htmlFor={`${mode}-password`}>Password</label>
            <input
              id={`${mode}-password`}
              className="field-input"
              type="password"
              name="password"
              minLength={8}
              value={currentForm.password}
              onChange={mode === 'login' ? updateLogin : updateRegister}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
            />

            {error && <div className="inline-error">{error}</div>}
            <button className="primary-action w-100" disabled={loading}>
              {loading ? 'Đang xử lý...' : mode === 'login' ? 'Vào workspace' : 'Tạo và vào workspace'}
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
