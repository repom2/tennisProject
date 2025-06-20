import {getMatchProbabilities} from "common/functions/matchProbabilities";
//import styles from './YourStyles.module.css';
import {getPlayerStatistics} from "common/functions/playerStatistics";
import PlayerStats from "components/PlayerStatistics/PlayerStatistics";
import styles from "components/Tips/Tips.module.css";
import {Bets} from "data/openapi";
import React, {useEffect, useState} from "react";
import {useQuery} from "react-query";

interface PlayerStats {
    playerSPW: number;
    playerRPW: number;
    playerMatches: number;
    matches: {
        date: string[];
        surface: string[];
        round_name: string[];
        tourney_name: string[];
        spw: number[];
        rpw: number[];
        opponent_name: string[];
        dr: number[];
        opponent_id: string[];
        opponent_hard: number[];
        opponent_clay: number[];
    };
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
                Home AH 6.5: {content.homeAH6_5}{" "}
                {content.homeAH6_5 ? (1 / content.homeAH6_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH6_5 ? (1 / (1 - content.homeAH6_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Home AH 5.5: {content.homeAH5_5}{" "}
                {content.homeAH5_5 ? (1 / content.homeAH5_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH5_5 ? (1 / (1 - content.homeAH5_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Home AH 4.5: {content.homeAH4_5}{" "}
                {content.homeAH4_5 ? (1 / content.homeAH4_5).toFixed(2) : "N/A"}{" "}
                {content.homeAH4_5 ? (1 / (1 - content.homeAH4_5)).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Home AH 3.5: {content.homeAH3_5}{" "}
                {content.homeAH3_5 ? (1 / content.homeAH3_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Home AH 2.5: {content.homeAH2_5}{" "}
                {content.homeAH2_5 ? (1 / content.homeAH2_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Away AH 6.5: {content.awayAH6_5}{" "}
                {content.awayAH6_5 ? (1 / content.awayAH6_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Away AH 5.5: {content.awayAH5_5}{" "}
                {content.awayAH5_5 ? (1 / content.awayAH5_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Away AH 4.5: {content.awayAH4_5}{" "}
                {content.awayAH4_5 ? (1 / content.awayAH4_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Away AH 3.5: {content.awayAH3_5}{" "}
                {content.awayAH3_5 ? (1 / content.awayAH3_5).toFixed(2) : "N/A"}
            </p>
            <p className={styles.NoWrap}>
                Away AH 2.5: {content.awayAH2_5}{" "}
                {content.awayAH2_5 ? (1 / content.awayAH2_5).toFixed(2) : "N/A"}
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

    // Query for player stats-based probabilities
    const {data: probabilities, refetch: refetchProbs} = useQuery(
        ["matchProbabilities", level, homeId, awayId],
        () => {
            // Only fetch if we have both player stats
            if (homeStats && awayStats) {
                // Log the structure to see what we're working with
                console.log("homeStats:", homeStats);
                console.log("awayStats:", awayStats);

                // Add detailed logging to understand the data structure
                console.log("homeStats.data structure:", JSON.stringify(homeStats.data));
                console.log("awayStats.data structure:", JSON.stringify(awayStats.data));

                // Access the data based on its actual structure
                // Use type assertion with unknown first to avoid TypeScript error
                const homePlayerStats = homeStats.data as unknown as PlayerStats;
                const awayPlayerStats = awayStats.data as unknown as PlayerStats;

                console.log("Home player stats:", homePlayerStats);

                return getMatchProbabilities({
                    level: level,
                    matchId: matchData.matchId,
                    homeSPW: homePlayerStats.playerSPW,
                    homeRPW: homePlayerStats.playerRPW,
                    awaySPW: awayPlayerStats.playerSPW,
                    awayRPW: awayPlayerStats.playerRPW,
                    surface: surface,
                });
            }
            return null;
        },
        {
            enabled: false, // disable automatic query
            refetchOnWindowFocus: false,
        }
    );

    // Query for season stats-based probabilities
    const {data: seasonProbs, isLoading: seasonProbsLoading} = useQuery(
        ["seasonMatchProbabilities", matchData.matchId],
        () => {
            const homeSPW =
                matchData.surface === "clay"
                    ? matchData.homeSpwClay
                    : matchData.surface === "grass"
                    ? matchData.homeSpwGrass
                    : matchData.homeSpw;
            const homeRPW =
                matchData.surface === "clay"
                    ? matchData.homeRpwClay
                    : matchData.surface === "grass"
                    ? matchData.homeRpwGrass
                    : matchData.homeRpw;
            const awaySPW =
                matchData.surface === "clay"
                    ? matchData.awaySpwClay
                    : matchData.surface === "grass"
                    ? matchData.awaySpwGrass
                    : matchData.awaySpw;
            const awayRPW =
                matchData.surface === "clay"
                    ? matchData.awayRpwClay
                    : matchData.surface === "grass"
                    ? matchData.awayRpwGrass
                    : matchData.awayRpw;

            return getMatchProbabilities({
                level: level,
                matchId: matchData.matchId,
                homeSPW: homeSPW,
                homeRPW: homeRPW,
                awaySPW: awaySPW,
                awayRPW: awayRPW,
                surface: matchData.surface,
            });
        },
        {
            enabled: !!matchData.matchId,
            refetchOnWindowFocus: false,
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
            console.log("Both player stats loaded, fetching probabilities");
            refetchProbs();
        }
    }, [homeStats?.data, awayStats?.data, refetchProbs]);

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
                    <td>{matchData.statsWinGrass}</td>
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
                    <td>
                        <div>
                            {matchData.homeSpwGrass}/{matchData.homeRpwGrass}
                        </div>
                        <div>
                            {matchData.awaySpwGrass}/{matchData.awayRpwGrass}
                        </div>
                    </td>
                    <td>
                        <div className={styles.NoWrap}>{matchData.homeMatchesGrass}</div>
                        <div className={styles.NoWrap}>{matchData.awayMatchesGrass}</div>
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
                    <td>{matchData.eloProbGrass}</td>
                    <td>
                        <div className={styles.NoWrap}>
                            {matchData.homeEloGrass} / {matchData.homeEloGrassGames}
                        </div>
                        <div className={styles.NoWrap}>
                            {matchData.awayEloGrass} / {matchData.awayEloGrassGames}
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
                        <td colSpan={21} style={{overflowX: "auto", minWidth: "100%"}}>
                            <div style={{width: "100%", overflowX: "auto"}}>
                                {/* Match probabilities from matchData */}
                                {/* Surface stats calculation - not rendered */}
                                {(() => {
                                    // This IIFE just calculates values but doesn't render anything
                                    const homeSPW =
                                        matchData.surface === "clay"
                                            ? matchData.homeSpwClay
                                            : matchData.surface === "grass"
                                            ? matchData.homeSpwGrass
                                            : matchData.homeSpw;
                                    const homeRPW =
                                        matchData.surface === "clay"
                                            ? matchData.homeRpwClay
                                            : matchData.surface === "grass"
                                            ? matchData.homeRpwGrass
                                            : matchData.homeRpw;
                                    const awaySPW =
                                        matchData.surface === "clay"
                                            ? matchData.awaySpwClay
                                            : matchData.surface === "grass"
                                            ? matchData.awaySpwGrass
                                            : matchData.awaySpw;
                                    const awayRPW =
                                        matchData.surface === "clay"
                                            ? matchData.awayRpwClay
                                            : matchData.surface === "grass"
                                            ? matchData.awayRpwGrass
                                            : matchData.awayRpw;
                                    // Store in component state or variable if needed
                                    return null;
                                })()}

                                {/* Season probabilities section */}
                                <div className={styles.probabilities}>
                                    <h3>Match Probabilities (Based on Season Stats)</h3>
                                    {seasonProbsLoading ? (
                                        <div>Loading season probabilities...</div>
                                    ) : seasonProbs ? (
                                        <>
                                            <div style={{marginBottom: "15px"}}>
                                                <strong>Match Win Probability:</strong>{" "}
                                                {seasonProbs?.data?.matchProb}
                                                {seasonProbs?.data?.matchProb &&
                                                    " (Odds: " +
                                                        (1 / seasonProbs.data.matchProb).toFixed(
                                                            2
                                                        ) +
                                                        ")"}
                                            </div>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    justifyContent: "flex-start",
                                                    gap: "20px",
                                                }}
                                            >
                                                {/* Over/Under column */}
                                                <div>
                                                    <h4>Over/Under</h4>
                                                    <div>
                                                        <strong>Games Over 21.5:</strong>{" "}
                                                        {seasonProbs?.data?.gamesOver21_5}
                                                        {seasonProbs?.data?.gamesOver21_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 /
                                                                    seasonProbs.data.gamesOver21_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div>
                                                        <strong>Games Over 22.5:</strong>{" "}
                                                        {seasonProbs?.data?.gamesOver22_5}
                                                        {seasonProbs?.data?.gamesOver22_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 /
                                                                    seasonProbs.data.gamesOver22_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div>
                                                        <strong>Games Over 23.5:</strong>{" "}
                                                        {seasonProbs?.data?.gamesOver23_5}
                                                        {seasonProbs?.data?.gamesOver23_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 /
                                                                    seasonProbs.data.gamesOver23_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                </div>

                                                {/* Home AH column */}
                                                <div>
                                                    <h4>Home Asian Handicap</h4>
                                                    <div>
                                                        <strong>Home AH 2.5:</strong>{" "}
                                                        {seasonProbs?.data?.homeAH2_5}
                                                        {seasonProbs?.data?.homeAH2_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.homeAH2_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div style={{display: "block"}}>
                                                        <strong>Home AH 3.5:</strong>{" "}
                                                        {seasonProbs?.data?.homeAH3_5}
                                                        {seasonProbs?.data?.homeAH3_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.homeAH3_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div>
                                                        <strong>Home AH 4.5:</strong>{" "}
                                                        {seasonProbs?.data?.homeAH4_5}
                                                        {seasonProbs?.data?.homeAH4_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.homeAH4_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                </div>

                                                {/* Away AH column */}
                                                <div>
                                                    <h4>Away Asian Handicap</h4>
                                                    <div>
                                                        <strong>Away AH 2.5:</strong>{" "}
                                                        {seasonProbs?.data?.awayAH2_5}
                                                        {seasonProbs?.data?.awayAH2_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.awayAH2_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div style={{display: "block"}}>
                                                        <strong>Away AH 3.5:</strong>{" "}
                                                        {seasonProbs?.data?.awayAH3_5}
                                                        {seasonProbs?.data?.awayAH3_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.awayAH3_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                    <div>
                                                        <strong>Away AH 4.5:</strong>{" "}
                                                        {seasonProbs?.data?.awayAH4_5}
                                                        {seasonProbs?.data?.awayAH4_5 &&
                                                            " (Odds: " +
                                                                (
                                                                    1 / seasonProbs.data.awayAH4_5
                                                                ).toFixed(2) +
                                                                ")"}
                                                    </div>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div>No season probabilities available</div>
                                    )}
                                </div>

                                {/* Match probabilities section */}
                                {probabilities && (
                                    <div className={styles.probabilities}>
                                        <h3>Match Probabilities (Based on Recent Form)</h3>
                                        <div style={{marginBottom: "15px"}}>
                                            <strong>Match Win Probability:</strong>{" "}
                                            {probabilities?.data?.matchProb}
                                            {probabilities?.data?.matchProb &&
                                                " (Odds: " +
                                                    (1 / probabilities.data.matchProb).toFixed(2) +
                                                    ")"}
                                        </div>
                                        <div
                                            style={{
                                                display: "flex",
                                                justifyContent: "flex-start",
                                                gap: "20px",
                                            }}
                                        >
                                            {/* Over/Under column */}
                                            <div>
                                                <h4>Over/Under</h4>
                                                <div>
                                                    <strong>Games Over 21.5:</strong>{" "}
                                                    {probabilities?.data?.gamesOver21_5}
                                                    {probabilities?.data?.gamesOver21_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.gamesOver21_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div>
                                                    <strong>Games Over 22.5:</strong>{" "}
                                                    {probabilities?.data?.gamesOver22_5}
                                                    {probabilities?.data?.gamesOver22_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.gamesOver22_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div>
                                                    <strong>Games Over 23.5:</strong>{" "}
                                                    {probabilities?.data?.gamesOver23_5}
                                                    {probabilities?.data?.gamesOver23_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.gamesOver23_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                            </div>

                                            {/* Home AH column */}
                                            <div>
                                                <h4>Home Asian Handicap</h4>
                                                <div>
                                                    <strong>Home AH 2.5:</strong>{" "}
                                                    {probabilities?.data?.homeAH2_5}
                                                    {probabilities?.data?.homeAH2_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.homeAH2_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div style={{display: "block"}}>
                                                    <strong>Home AH 3.5:</strong>{" "}
                                                    {probabilities?.data?.homeAH3_5}
                                                    {probabilities?.data?.homeAH3_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.homeAH3_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div>
                                                    <strong>Home AH 4.5:</strong>{" "}
                                                    {probabilities?.data?.homeAH4_5}
                                                    {probabilities?.data?.homeAH4_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.homeAH4_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                            </div>

                                            {/* Away AH column */}
                                            <div>
                                                <h4>Away Asian Handicap</h4>
                                                <div>
                                                    <strong>Away AH 2.5:</strong>{" "}
                                                    {probabilities?.data?.awayAH2_5}
                                                    {probabilities?.data?.awayAH2_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.awayAH2_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div style={{display: "block"}}>
                                                    <strong>Away AH 3.5:</strong>{" "}
                                                    {probabilities?.data?.awayAH3_5}
                                                    {probabilities?.data?.awayAH3_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.awayAH3_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                                <div>
                                                    <strong>Away AH 4.5:</strong>{" "}
                                                    {probabilities?.data?.awayAH4_5}
                                                    {probabilities?.data?.awayAH4_5 &&
                                                        " (Odds: " +
                                                            (
                                                                1 / probabilities.data.awayAH4_5
                                                            ).toFixed(2) +
                                                            ")"}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div style={{marginTop: "20px", marginBottom: "20px"}}>
                                    <h3
                                        style={{
                                            borderBottom: "2px solid #4a90e2",
                                            paddingBottom: "8px",
                                            color: "#2c3e50",
                                        }}
                                    >
                                        {matchData.homeName} - Player Statistics
                                    </h3>
                                    <div
                                        style={{
                                            padding: "15px",
                                            backgroundColor: "#f8f9fa",
                                            borderRadius: "8px",
                                            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                                        }}
                                    >
                                        {homeStats ? (
                                            <PlayerStats data={homeStats} />
                                        ) : (
                                            <p>Loading player statistics...</p>
                                        )}
                                    </div>
                                </div>

                                <div style={{marginTop: "20px", marginBottom: "20px"}}>
                                    <h3
                                        style={{
                                            borderBottom: "2px solid #e74c3c",
                                            paddingBottom: "8px",
                                            color: "#2c3e50",
                                        }}
                                    >
                                        {matchData.awayName} - Player Statistics
                                    </h3>
                                    <div
                                        style={{
                                            padding: "15px",
                                            backgroundColor: "#f8f9fa",
                                            borderRadius: "8px",
                                            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                                        }}
                                    >
                                        {awayStats ? (
                                            <PlayerStats data={awayStats} />
                                        ) : (
                                            <p>Loading player statistics...</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                )}
            </React.Fragment>
        </>
    );
};

export default Dropdown;
