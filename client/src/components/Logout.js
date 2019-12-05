import React, { Component } from 'react'
import { Route } from 'react-router-dom'

import cookie from 'react-cookies';
import { Redirect } from 'react-router-dom'


class Logout extends Component {
    constructor() {
        super()
        this.logOut()

    }

    logOut () {
        cookie.remove("token", {path: "/"})
        cookie.remove("chats", {path: "/"})

    }

    componentDidMount() {
        window.location.reload()
    }


    render () {
        return (<Redirect to={{pathname: "/"}}/>)

    }
}
export default Logout