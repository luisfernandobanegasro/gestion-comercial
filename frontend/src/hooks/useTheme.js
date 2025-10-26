import { useEffect, useState } from 'react'
export default function useTheme(){
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')
  useEffect(()=>{
    localStorage.setItem('theme', theme)
    document.documentElement.className = theme === 'light' ? 'theme-light' : ''
  }, [theme])
  return { theme, toggle: ()=> setTheme(t => t==='dark' ? 'light' : 'dark') }
}
