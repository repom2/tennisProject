import React from "react";
import {Link} from "react-router-dom";

import styles from "./Sidebar.module.css";

const Sidebar: React.FC = () => {
    return (
        <div className={styles.sidebar}>
            <h2 className={styles.menuTitle}>Sport Menu</h2>
            <ul className={styles.list}>
                <li>
                    <Link to="/tips-wta" className={styles.link}>
                        <div className={styles.button}>Tennis WTA</div>
                    </Link>
                    <Link to="/tips-atp" className={styles.link}>
                        <div className={styles.button}>Tennis ATP</div>
                    </Link>
                </li>
                <li>
                    <Link to="/footballtips" className={styles.link}>
                        <div className={styles.button}>Football</div>
                    </Link>
                </li>
                <li>
                    <Link to="/elo" className={styles.link}>
                        <div className={styles.button}>Elo Ratings</div>
                    </Link>
                </li>
                <li>
                    <Link to="/match-probability" className={styles.link}>
                        <div className={styles.button}>Match Calculator</div>
                    </Link>
                </li>
            </ul>
        </div>
    );
};

export default Sidebar;
