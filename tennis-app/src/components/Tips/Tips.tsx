import {getData} from "common/functions/betData";
import {getPlayerStatistics} from "common/functions/playerStatistics";
import Dropdown from "components/Dropdown/Dropdown";
import {Bets} from "data/openapi";
import React, {useState} from "react";
import {useQuery} from "react-query";

import styles from "./Tips.module.css";

interface RenderTextProps {
    text?: string;
}

// Render openAI response's new lines and bullet points appropriately
const RenderText: React.FC<RenderTextProps> = ({text}) => {
    if (!text) {
        return null;
    }
    const htmlText = text.replace(/\n/g, "<br />").replace(/\n-\s/g, "<li>");
    return <div dangerouslySetInnerHTML={{__html: htmlText}} />;
};

interface TipsProps {
    level: string;
}

interface TooltipProps {
    children: React.ReactNode;
    content: Bets;
}

// Custom Tooltip component
const Tooltip = ({children, content}: TooltipProps) => {
    const [isVisible, setIsVisible] = useState(false);

    const showTooltip = () => setIsVisible(true);
    const hideTooltip = () => setIsVisible(false);

    // Conditionally apply the 'visible' class to show the tooltip
    const tooltipClass = isVisible ? `${styles.tooltipText} ${styles.visible}` : styles.tooltipText;

    const probabilities = (
        <div>
            <div className={styles.NoWrap}>
                Over 21.5 Games: {content.gamesOver21_5}{" "}
                {content.gamesOver21_5 ? (1 / content.gamesOver21_5).toFixed(2) : "N/A"}
            </div>
            <p className={styles.NoWrap}>
                Over 22.5 Games: {content.gamesOver22_5}{" "}
                {content.gamesOver22_5 ? (1 / content.gamesOver22_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Over 23.5 Games: {content.gamesOver23_5}{" "}
                {content.gamesOver23_5 ? (1 / content.gamesOver23_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 6.5: {content.homeAH6_5}{" "}
                {content.homeAH6_5 ? (1 / content.homeAH6_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH6_5 ? (1 / (1 - content.homeAH6_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 5.5: {content.homeAH5_5}{" "}
                {content.homeAH5_5 ? (1 / content.homeAH5_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH5_5 ? (1 / (1 - content.homeAH5_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 4.5: {content.homeAH4_5}{" "}
                {content.homeAH4_5 ? (1 / content.homeAH4_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH4_5 ? (1 / (1 - content.homeAH4_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 3.5: {content.homeAH3_5}{" "}
                {content.homeAH3_5 ? (1 / content.homeAH3_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 2.5: {content.homeAH2_5}{" "}
                {content.homeAH2_5 ? (1 / content.homeAH2_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                AH 1.5 Set: {content.homeWin1Set}{" "}
                {content.homeWin1Set ? (1 / content.homeWin1Set).toFixed(2) : "N/A"}
            </p>
        </div>
    );
    return (
        <div
            className={styles.tooltipContainer}
            onMouseEnter={showTooltip}
            onMouseLeave={hideTooltip}
        >
            {children}
            <div className={tooltipClass}>{probabilities}</div>
        </div>
    );
};

export const Tips: React.FC<TipsProps> = ({level}) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleRowClick = (index: number) => {
        setOpenIndex(index === openIndex ? null : index);
    };

    const {isLoading, isError, data} = useQuery(["bets", level], () => getData({level}));

    if (isLoading) return <div />;

    if (isError) return <div />;

    const tooltipContent = (
        <div>
            <p>Over 21.5 Games: </p>
            <p>Over 22.5 Games: </p>
            <p>Over 23.5 Games: </p>
            {/* Add more stats as needed */}
        </div>
    );

    return (
        <div className={styles.main}>
            <table className={styles.table}>
                <thead>
                    <tr className={styles.header}>
                        <th>Match</th>
                        <th>Yield</th>
                        <th>Dr</th>
                        <th>Odds</th>
                        <th>StatsWin</th>
                        <th>Hard%</th>
                        <th>Clay%</th>
                        <th>Grass%</th>
                        <th>S/RPW</th>
                        <th>Matches</th>
                        <th>S/RPW(Clay)</th>
                        <th>MClay</th>
                        <th>S/RPW(Grass)</th>
                        <th>MGrass</th>
                        <th>EloHard</th>
                        <th />
                        <th>EloClay</th>
                        <th />
                        <th>EloGrass</th>
                        <th />
                        <th>YElo</th>
                        <th>MLProb</th>
                        <th>H2H%</th>
                        <th>COpp%</th>
                        <th>Start</th>
                    </tr>
                </thead>
                <tbody>
                    {data &&
                        data.data &&
                        data.data.map((matchData: Bets, index: number) => (
                            <Dropdown
                                key={index}
                                openIndex={openIndex}
                                index={index}
                                matchData={matchData}
                                level={level}
                                handleRowClick={handleRowClick}
                            />
                        ))}
                </tbody>
            </table>
        </div>
    );
};
