import "./Tips.css";

import {getData} from "common/functions/betData";
import {Bets} from "data/openapi";
import React, {useEffect, useState} from "react";
import {useQuery} from "react-query";

export const Tips: React.FC = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleItemClick = (index: number) => {
        if (openIndex === index) {
            setOpenIndex(null); // close if already open
        } else {
            setOpenIndex(index); // open clicked item
        }
    };
    const {isLoading, isError, data, error} = useQuery("bets", getData);

    if (isLoading) return <div />;

    if (isError) return <div />;

    return (
        <div className="main">
            <ul className="player-list">
                <li className="player-list-item player-list-item-header">
                    <div>
                        <strong>Home</strong>
                    </div>
                    <div>
                        <strong>Away</strong>
                    </div>
                    <div>
                        <strong>1</strong>
                    </div>
                    <div>
                        <strong>2</strong>
                    </div>
                    <div>
                        <strong>Elo</strong>
                    </div>
                    <div>
                        <strong>YElo</strong>
                    </div>
                    <div>
                        <strong>Win%</strong>
                    </div>
                    <div>
                        <strong>H2H%</strong>
                    </div>
                    <div>
                        <strong>COpp%</strong>
                    </div>
                    <div>
                        <strong>S/RPW1</strong>
                    </div>
                    <div>
                        <strong>S/RPW2</strong>
                    </div>
                </li>
                {data &&
                    data.data &&
                    data.data.map((player: Bets, index: number) => (
                        <React.Fragment key={player.matchId}>
                            <li
                                key={player.matchId}
                                className="player-list-item"
                                onClick={() => handleItemClick(index)}
                            >
                                <div>{player.homeName}</div>
                                <div>{player.awayName}</div>
                                <div>{player.homeOdds}</div>
                                <div>{player.awayOdds}</div>
                                <div>{player.eloProb}</div>
                                <div>{player.yearEloProb}</div>
                                <div>{player.statsWin}</div>
                                <div>
                                    {player.h2hWin}/{player.h2hMatches}
                                </div>
                                <div>
                                    {player.commonOpponents}/{player.commonOpponentsCount}
                                </div>
                                <div>
                                    {player.homeSpw}/{player.homeRpw}
                                </div>
                                <div>
                                    {player.awaySpw}/{player.awayRpw}
                                </div>
                            </li>
                            {openIndex === index && (
                                <li>
                                    {/* Whatever you want to display when clicked */}
                                    <div>{player.preview}</div>
                                    <div>{player.reasoning}</div>
                                </li>
                            )}
                        </React.Fragment>
                    ))}
            </ul>
        </div>
    );
};
