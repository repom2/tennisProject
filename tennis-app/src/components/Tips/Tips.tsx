import "./Tips.css";

import {getData} from "common/functions/betData";
import {Bets} from "data/openapi";
import React, {useState} from "react";
import {useQuery} from "react-query";

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

export const Tips: React.FC<TipsProps> = ({level}) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleItemClick = (index: number) => {
        setOpenIndex(index === openIndex ? null : index);
    };
    const {isLoading, isError, data} = useQuery(['bets', level], () => getData({level}));

    if (isLoading) return <div />;

    if (isError) return <div />;

    return (
        <div className="main">
            <table className="table">
                <thead>
                    <tr className="header">
                        <th>Match</th>
                        <th>Yield</th>
                        <th>Dr</th>
                        <th>Odds</th>
                        <th>StatsWin%</th>
                        <th>S/RPW1</th>
                        <th>Matches</th>
                        <th>S/RPW2</th>
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
                        data.data.map((player: Bets, index: number) => (
                            <React.Fragment key={index}>
                                <tr
                                    key={player.matchId}
                                    className="row"
                                    onClick={() => handleItemClick(index)}
                                >
                                    <td>
                                        <div className="no-wrap">{player.homeName} ({player.homeCurrentRank})</div>
                                        <div className="no-wrap">{player.awayName} ({player.awayCurrentRank})</div>
                                    </td>
                                    <td>
                                        <div>{player.homeYield}</div>
                                        <div>{player.awayYield}</div>
                                    </td>
                                    <td>
                                        <div>{player.homeDr}</div>
                                        <div>{player.awayDr}</div>
                                    </td>
                                    <td>
                                        <div>{player.homeOdds}</div>
                                        <div>{player.awayOdds}</div>
                                    </td>
                                    <td>{player.statsWin}</td>
                                    <td>
                                        {player.homeSpw}/{player.homeRpw}
                                    </td>
                                    <td className="no-wrap">{player.homeMatches}</td>
                                    <td>
                                        {player.awaySpw}/{player.awayRpw}
                                    </td>
                                    <td className="no-wrap">{player.awayMatches}</td>
                                    <td>{player.eloProb}</td>
                                    <td>{player.yearEloProb}</td>
                                    <td>{player.homeProb}</td>
                                    <td>
                                        {player.h2hWin}/{player.h2hMatches}
                                    </td>
                                    <td>
                                        {player.commonOpponents}/{player.commonOpponentsCount}
                                    </td>
                                    <td>
                                        {player.startAt
                                            ? new Date(player.startAt).toLocaleDateString()
                                            : "N/A"}
                                    </td>
                                </tr>
                                {openIndex === index && (
                                    <tr>
                                        <td colSpan={15}>
                                            {/* Whatever you want to display when clicked */}
                                            <div className="Preview">
                                                <div><h2>{player.homeName}</h2></div>
                                                <div className="Preview">{player.homePlayerInfo}{player.homePlays}</div>
                                                <RenderText text={player.homeShortPreview} />
                                                <div className="PreviewTable">
                                                    <RenderText text={player.homeTable} />
                                                </div>
                                            </div>
                                            <div className="Preview">
                                                <h2>{player.awayName}</h2>
                                                <div className="Preview">{player.awayPlayerInfo}{player.awayPlays}</div>
                                                <RenderText text={player.awayShortPreview} />
                                                <div className="PreviewTable">
                                                    <RenderText text={player.awayTable} />
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
