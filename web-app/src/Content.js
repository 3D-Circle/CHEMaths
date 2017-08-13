import React, {Component} from 'react';
import PropTypes from 'prop-types';
import MoleculePane from './Panes/Molecule';
import EquationPane from './Panes/Equation';



const tab_config = {
    molecule: {
        name: 'Molecule Info',
        component: <MoleculePane/>
    },
    equation: {
        name: "Balance Equation",
        component: <EquationPane/>
    }
};


export default class Content extends Component {
    constructor() {
        super();
        this.state = {
            'currentPane': 'molecule'
        };
        this.changePane = this.changePane.bind(this);
    }

    changePane(e) {
        this.setState({
            'currentPane': e.target.getAttribute('data-tab-target')
        });
    }

    render() {
        return (
            <div id="content_wrapper">
                <TabList config={tab_config}
                         tabChangeCallback={this.changePane}
                         currentPane={this.state.currentPane}/>
                <TabPaneWrapper currentPane={this.state.currentPane}/>
            </div>
        );
    }
}


class TabList extends Component {
    render() {
        return (
            <div id="tab_list">
                {Object.keys(this.props.config).map(
                    (id, index) => <Tab key={index}
                                        tabTargetId={id}
                                        text={this.props.config[id].name}
                                        tabChangeCallback={this.props.tabChangeCallback}
                                        currentPane={this.props.currentPane} />
                )}
            </div>
        );
    }
}

TabList.PropTypes = {
    config: PropTypes.object,
    tabChangeCallback: PropTypes.func,
    currentPane: PropTypes.string
};


class Tab extends Component {
    render() {
        return (
            <div className={
                    this.props.tabTargetId === this.props.currentPane ? 'tab current' : 'tab'
                 }
                 onClick={this.props.tabChangeCallback}
                 data-tab-target={this.props.tabTargetId}>
                {this.props.text}
            </div>
        )
    }
}

Tab.PropTypes = {
    text: PropTypes.string,
    tabTargetId: PropTypes.string
};


class TabPaneWrapper extends Component {
    render() {
        return (
            tab_config[this.props.currentPane].component
        )
    }
}

TabPaneWrapper.PropTypes = {
    currentPane: PropTypes.string
};
