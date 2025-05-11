import React, {useState, useEffect} from "react";
import {useQuery} from "react-query";
//import styles from './YourStyles.module.css';
import {getPlayerStatistics} from "common/functions/playerStatistics";
import {getMatchProbabilities} from "common/functions/matchProbabilities";
import PlayerStats from "components/PlayerStatistics/PlayerStatistics";
import styles from "components/Tips/Tips.module.css";
import {Bets} from "data/openapi";

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

interface DropdownProps {
    openIndex: number | null;
    index: number;
    matchData: Bets;
    level: string;
    handleRowClick: (index: number) => void;
}



const Dropdown = ({openIndex, index, matchData, level, handleRowClick}: DropdownProps) => {
    const [homeId, setHomeId] = useState(null);
    const [awayId, setAwayId] = useState(null);
    const [surface, setSurface] = useState(null);

    const {data: homeStats, refetch: reFetch} = useQuery(
        ["statistics", level, homeId],
        () => getPlayerStatistics({level: level, playerId: homeId, surface: surface}),
        {
            enabled: false, // disable automatic query on mount
        }
    );

    const {data: awayStats, refetch: reFetchAway} = useQuery(
        ["statistics", level, awayId],
        () => getPlayerStatistics({level: level, playerId: awayId, surface: surface}),
        {
            enabled: false, // disable automatic query on mount
        }
    );

    const {data: probabilities, refetch: refetchProbs} = useQuery(
        ["matchProbabilities", level, homeId, awayId],
        () => {
            // Only fetch if we have both player stats
            if (homeStats && awayStats) {
                // Log the structure to see what we're working with
                console.log("homeStats:", homeStats);
                console.log("awayStats:", awayStats);
                
                // Access the nested data structure correctly
                const homePlayerStats: PlayerStats = homeStats.data;
                const awayPlayerStats: PlayerStats = awayStats.data;
                
                console.log("Home player stats:", homePlayerStats);
                
                return getMatchProbabilities({
                    level: level,
                    matchId: matchData.matchId,
                    homeSPW: homePlayerStats[0].playerSPW,
                    homeRPW: homePlayerStats[0].playerRPW,
                    awaySPW: awayPlayerStats[0].playerSPW,
                    awayRPW: awayPlayerStats[0].playerRPW,
                    surface: surface
                });
            }
            return null;
        },
        {
            enabled: false, // disable automatic query
            refetchOnWindowFocus: false
        }
    );

    console.log(matchData);

    useEffect(() => {
        if (openIndex === index && homeId) {
            reFetch();
        }
    }, [openIndex, index, homeId, reFetch]);

    useEffect(() => {
        if (openIndex === index && awayId) {
            reFetchAway();
        }
    }, [openIndex, index, awayId, reFetchAway]);

    // Add effect to trigger probability calculation when both player stats are loaded
    useEffect(() => {
        if (homeStats && awayStats) {
            refetchProbs();
        }
    }, [homeStats, awayStats, refetchProbs]);

    const handleRowClickWithPlayerId = (homeId: any, awayId: any, surface: any) => {
        setHomeId(homeId);
        setAwayId(awayId);
        setSurface(surface);
        handleRowClick(index);
    };

    return (
        <>
            <React.Fragment key={index}>
                <tr
                    key={matchData.matchId}
                    className={styles.row}
                    onClick={() =>
                        handleRowClickWithPlayerId(
                            matchData.homeId,
                            matchData.awayId,
                            matchData.surface
                        )
                    }
                >
                    <td>
                        <div className={styles.NoWrap}>
                            {matchData.homeName} ({matchData.homeCurrentRank})
                        </div>
                        <div className={styles.NoWrap}>
                            {matchData.awayName} ({matchData.awayCurrentRank})
                        </div>
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
                    <td>{matchData.statsWinHard}</td>
                    <td>{matchData.statsWinClay}</td>
                    <td>
                        <Tooltip content={matchData}>
                            <span>Show</span>
                        </Tooltip>
                    </td>
                    <td>
                        <div>
                            {matchData.homeSpw}/{matchData.homeRpw}
                        </div>
                        <div>
                            {matchData.awaySpw}/{matchData.awayRpw}
                        </div>
                    </td>
                    <td>
                        <div className={styles.NoWrap}>{matchData.homeMatches}</div>
                        <div className={styles.NoWrap}>{matchData.awayMatches}</div>
                    </td>
                    <td>
                        <div>
                            {matchData.homeSpwClay}/{matchData.homeRpwClay}
                        </div>
                        <div>
                            {matchData.awaySpwClay}/{matchData.awayRpwClay}
                        </div>
                    </td>
                    <td>
                        <div className={styles.NoWrap}>{matchData.homeMatchesClay}</div>
                        <div className={styles.NoWrap}>{matchData.awayMatchesClay}</div>
                    </td>
                    <td>{matchData.eloProbHard}</td>
                    <td>
                        <div className={styles.NoWrap}>
                            {matchData.homeEloHard} / {matchData.homeEloHardGames}
                        </div>
                        <div className={styles.NoWrap}>
                            {matchData.awayEloHard} / {matchData.awayEloHardGames}
                        </div>
                    </td>
                    <td>{matchData.eloProbClay}</td>
                    <td>
                        <div className={styles.NoWrap}>
                            {matchData.homeEloClay} / {matchData.homeEloClayGames}
                        </div>
                        <div className={styles.NoWrap}>
                            {matchData.awayEloClay} / {matchData.awayEloClayGames}
                        </div>
                    </td>
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
                        <td colSpan={21} style={{ overflowX: "auto", minWidth: "100%" }}>
                            <div style={{ width: "100%", overflowX: "auto" }}>
                                <h3>{matchData.homeName}</h3>
                                <div>
                                    {homeStats ? <PlayerStats data={homeStats} /> : <p>Loading...</p>}
                                </div>
                                <h2>{matchData.awayName}</h2>
                                <div>
                                    {awayStats ? <PlayerStats data={awayStats} /> : <p>Loading...</p>}
                                </div>
                                
                                {/* Add this section to display match probabilities */}
                                {probabilities && (
                                    <div className={styles.probabilities}>
                                        <h3>Match Probabilities (Based on Recent Form)</h3>
                                        <div className={styles.probabilityGrid}>
                                            <div>
                                                <strong>Match Win Probability:</strong> {probabilities.data.matchProb}
                                            </div>
                                            <div>
                                                <strong>Games Over 21.5:</strong> {probabilities.data.gamesOver21_5}
                                            </div>
                                            <div>
                                                <strong>Games Over 22.5:</strong> {probabilities.data.gamesOver22_5}
                                            </div>
                                            <div>
                                                <strong>Games Over 23.5:</strong> {probabilities.data.gamesOver23_5}
                                            </div>
                                            <div>
                                                <strong>Home AH 2.5:</strong> {probabilities.data.homeAH2_5}
                                            </div>
                                            <div>
                                                <strong>Home AH 3.5:</strong> {probabilities.data.homeAH3_5}
                                            </div>
                                            <div>
                                                <strong>Home AH 4.5:</strong> {probabilities.data.homeAH4_5}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </td>
                    </tr>
                )}
            </React.Fragment>
        </>
    );
};

export default Dropdown;
