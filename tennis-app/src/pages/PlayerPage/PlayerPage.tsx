import PageMainContent from "components/PageMainContent/PageMainContent";
import {useGetPlayers} from "pages/PlayerPage/hooks";
import {ReactElement} from "react";

import styles from "./PlayerPage.module.css";

const PlayerPage = (): ReactElement => {
    //const timeScale = useTimescale();
    const {data: players} = useGetPlayers();

    return (
        <>
            <PageMainContent className={styles.PlayerPage}>
                <div />
            </PageMainContent>
        </>
    );
};

export default PlayerPage;
