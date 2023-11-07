/*
 *  Container for the page main content.
 */
import {ReactElement, ReactNode} from "react";

import styles from "./PageMainContent.module.css";

interface IPageMainContentProps {
    children: ReactNode;
    className?: string;
    loading?: boolean;
}

const PageMainContent = ({children, className, loading}: IPageMainContentProps): ReactElement => {
    return (
        <main >
            <div></div>
        </main>
    );
};

export default PageMainContent;
