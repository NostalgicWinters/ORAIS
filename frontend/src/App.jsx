import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import TopBar from './components/TopBar'
import Dashboard from './components/Dashboard'
import Overview from './tabs/Overview'

function App() {

  return (
    <div>
      <Dashboard />
    </div>
   
  )
}

export default App
