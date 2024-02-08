import "./Tips.css";

import {getData} from "common/functions/betData";
import {Bets} from "data/openapi";
import React, {useEffect, useState} from "react";
import {useQuery} from "react-query";

export const Tips: React.FC = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleItemClick = (index: number) => {
        setOpenIndex(index === openIndex ? null : index);
    };
    const {isLoading, isError, data, error} = useQuery("bets", getData);

    if (isLoading) return <div />;

    if (isError) return <div />;

    return (
        <div className="main">
            <table className="table">
            <thead>
                <tr className="header">
                    <th>Match</th>
                    <th>Odds</th>
                    <th>Yield</th>
                    <th>Prob</th>
                    <th>Elo</th>
                    <th>YElo</th>
                    <th>Win%</th>
                    <th>H2H%</th>
                    <th>COpp%</th>
                    <th>S/RPW1</th>
                    <th>S/RPW2</th>
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
                                  <div>{player.homeName}</div>
                                  <div>{player.awayName}</div>
                                </td>
                                <td>
                                  <div>{player.homeOdds}</div>
                                  <div>{player.awayOdds}</div>
                                </td>
                                <td>
                                  <div>{player.homeYield}</div>
                                  <div>{player.awayYield}</div>
                                </td>
                                <td>{player.homeProb}</td>
                                <td>{player.eloProb}</td>
                                <td>{player.yearEloProb}</td>
                                <td>{player.statsWin}</td>
                                <td>
                                    {player.h2hWin}/{player.h2hMatches}
                                </td>
                                <td>
                                    {player.commonOpponents}/{player.commonOpponentsCount}
                                </td>
                                <td>
                                    {player.homeSpw}/{player.homeRpw}
                                </td>
                                <td>
                                    {player.awaySpw}/{player.awayRpw}
                                </td>
                            </tr>
                            {openIndex === index && (
                                <tr>
                                    <td colSpan={11} >
                                        {/* Whatever you want to display when clicked */}
                                        <div>{player.preview}</div>
                                        <div>{player.reasoning}</div>
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
