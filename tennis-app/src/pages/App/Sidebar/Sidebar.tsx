import styles from "./Sidebar.module.css";

import React from "react";
import {Link} from "react-router-dom";

const Sidebar: React.FC = () => {
    return (
        <div className={styles.sidebar}>
          <h2 className={styles.menuTitle}>Tennis Menu</h2>
          <ul className={styles.list}>
            <li>
            <Link to="/tips" className={styles.link}>
              <div className={styles.button}>Previews</div>
            </Link>
            </li>
            <li>
              <Link to="/elo" className={styles.link}>
               <div className={styles.button}>Elo Ratings</div>
              </Link>
            </li>
          </ul>
        </div>
    );
};

export default Sidebar;
