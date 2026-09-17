import { useState } from 'react'
import { useNavigate, Link } from 'react-router'
import "../auth.form.scss"
import { useAuth } from '../../../hooks/useAuth'

const Register = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { loading, handleRegister } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await handleRegister({ fullName, email, password });
    navigate("/");
  }

  if (loading) {
    return (<main><h1>Loading...</h1></main>);
  }

  return (
    <main>
      <div className="form-container">
        <h1>Sign Up</h1>
        <form onSubmit={handleSubmit}>
          <div className='input-group'>
            <label htmlFor='fullName'>Full Name</label>
            <input onChange={(e) => setFullName(e.target.value)} type='text' id='fullName' name='fullName' placeholder='Enter your full name' />
          </div>
          <div className='input-group'>
            <label htmlFor='email'>Email</label>
            <input onChange={(e) => setEmail(e.target.value)} type='email' id='email' name='email' placeholder='Enter email address' />
          </div>
          <div className='input-group'>
            <label htmlFor='password'>Password</label>
            <input onChange={(e) => setPassword(e.target.value)} type='password' id='password' name='password' placeholder='Enter password' />
          </div>
          <button className='button primary-button'>Sign Up</button>
        </form>
        <p>Already have an account? <Link to="/login">Login</Link></p>
      </div>
    </main>
  )
}

export default Register