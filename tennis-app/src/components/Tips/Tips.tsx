import {getData} from "common/functions/betData";
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
const Tooltip = ({ children, content }: TooltipProps) => {
  console.log("children", children)
  console.log("content", content)
  const [isVisible, setIsVisible] = useState(false);

  const showTooltip = () => setIsVisible(true);
  const hideTooltip = () => setIsVisible(false);

  // Conditionally apply the 'visible' class to show the tooltip
  const tooltipClass = isVisible ? `${styles.tooltipText} ${styles.visible}` : styles.tooltipText;

  const probabilities = (
    <div>
      <div className={styles.NoWrap}>Over 21.5 Games: {content.gamesOver21_5} {content.gamesOver21_5 ? (1 / content.gamesOver21_5).toFixed(2) : 'N/A'}</div>
      <p className={styles.NoWrap}>Over 22.5 Games: {content.gamesOver22_5} {content.gamesOver22_5 ? (1 / content.gamesOver22_5).toFixed(2) : 'N/A'}</p>
      <p className={styles.NoWrap}>Over 23.5 Games: {content.gamesOver23_5} {content.gamesOver23_5 ? (1 / content.gamesOver23_5).toFixed(2) : 'N/A'}</p>
      <p className={styles.NoWrap}>AH 4.5: {content.homeAH4_5} {content.homeAH4_5 ? (1 / content.homeAH4_5).toFixed(2) : 'N/A'}</p>
      <p className={styles.NoWrap}>AH 3.5: {content.homeAH3_5} {content.homeAH3_5 ? (1 / content.homeAH3_5).toFixed(2) : 'N/A'}</p>
      <p className={styles.NoWrap}>AH 2.5: {content.homeAH2_5} {content.homeAH2_5 ? (1 / content.homeAH2_5).toFixed(2) : 'N/A'}</p>
      <p className={styles.NoWrap}>AH 1.5 Set: {content.homeWin1Set} {content.homeWin1Set ? (1 / content.homeWin1Set).toFixed(2) : 'N/A'}</p>
    </div>
    )
  return (
    <div className={styles.tooltipContainer} onMouseEnter={showTooltip} onMouseLeave={hideTooltip}>
      {children}
      <div className={tooltipClass}>{probabilities}</div>
    </div>
  );
};

export const Tips: React.FC<TipsProps> = ({level}) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleItemClick = (index: number) => {
        setOpenIndex(index === openIndex ? null : index);
    };
    const {isLoading, isError, data} = useQuery(['bets', level], () => getData({level}));

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
                        <th>Win%</th>
                        <th>Show</th>
                        <th>S/RPW</th>
                        <th>Matches</th>
                        <th>Elo</th>
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
                            <React.Fragment key={index}>
                                <tr
                                    key={matchData.matchId}
                                    className={styles.row}
                                    onClick={() => handleItemClick(index)}
                                >
                                    <td>
                                        <div className={styles.NoWrap}>{matchData.homeName} ({matchData.homeCurrentRank})</div>
                                        <div className={styles.NoWrap}>{matchData.awayName} ({matchData.awayCurrentRank})</div>
                                    </td>
                                    <td>
                                        <div>{matchData.homeYield}</div>
                                        <div>{matchData.awayYield}</div>
                                    </td>
                                    <td>
                                        <div>{matchData.homeDr}</div>
                                        <div>{matchData.awayDr}</div>
                                    </td>
                                    <td>
                                        <div>{matchData.homeOdds}</div>
                                        <div>{matchData.awayOdds}</div>
                                    </td>
                                    <td>{matchData.statsWin}</td>
                                    <td>
                                        <Tooltip content={matchData}>
                                            <span>Show</span>
                                        </Tooltip>
                                    </td>
                                    <td>
                                        <div>{matchData.homeSpw}/{matchData.homeRpw}</div>
                                        <div>{matchData.awaySpw}/{matchData.awayRpw}</div>
                                    </td>
                                    <td>
                                        <div className={styles.NoWrap}>{matchData.homeMatches}</div>
                                        <div className={styles.NoWrap}>{matchData.awayMatches}</div>
                                    </td>
                                    <td>{matchData.eloProb}</td>
                                    <td>{matchData.yearEloProb}</td>
                                    <td>{matchData.homeProb}</td>
                                    <td>
                                        {matchData.h2hWin}/{matchData.h2hMatches}
                                    </td>
                                    <td>
                                        {matchData.commonOpponents}/{matchData.commonOpponentsCount}
                                    </td>
                                    <td>
                                        {matchData.startAt
                                            ? new Date(matchData.startAt).toLocaleDateString()
                                            : "N/A"}
                                    </td>
                                </tr>
                                {openIndex === index && (
                                    <tr>
                                        <td colSpan={13}>
                                            {/* Whatever you want to display when clicked */}
                                            <div className={styles.Preview}>
                                                <div><h2>{matchData.homeName}</h2></div>
                                                <div className={styles.Preview}>{matchData.homePlayerInfo}{matchData.homePlays}</div>
                                                <RenderText text={matchData.homeShortPreview} />
                                                <div className={styles.PreviewTable}>
                                                    <RenderText text={matchData.homeTable} />
                                                </div>
                                            </div>
                                            <div className={styles.Preview}>
                                                <h2>{matchData.awayName}</h2>
                                                <div className={styles.Preview}>{matchData.awayPlayerInfo}{matchData.awayPlays}</div>
                                                <RenderText text={matchData.awayShortPreview} />
                                                <div className={styles.PreviewTable}>
                                                    <RenderText text={matchData.awayTable} />
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                </tbody>
            </table>
        </div>
    );
};
