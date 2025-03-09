import React from 'react'
import styles from './title.module.css'

export default function Title ({ title }: { title: string }) {
  return <h1 className={styles.title}>{title}</h1>
}
