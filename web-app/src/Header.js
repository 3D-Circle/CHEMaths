import React, {Component} from 'react'
//import {FormControl} from 'react-bootstrap';


export default class Header extends Component {
    render() {
        return (
            <div id="input_wrapper">
                <SyntaxCheckStatus/>
                <InputBar/>
                <SubmitButton/>
            </div>
        )
    }
}


class SyntaxCheckStatus extends Component {
    render() {
        //TODO: Check whether we can do a less obtrusive syntax checker
        return <div id="syntax_check_status"/>
    }
}


class InputBar extends Component {
    render() {
        return (
            //Should react-bootstrap's FormControl be used ?
            <input type="text" id="main_input"/>
        )
    }
}


class SubmitButton extends Component {
    render() {
        return (
            <button id="submit_button"/>
        )
    }
}