import React, { Component } from 'react'
import cookie from 'react-cookies';

import { Redirect } from 'react-router-dom'


class Chats extends Component {
    constructor() {
        super()
        this.state = {
            message: '',
            path: ''
        }
    }

    componentDidMount(){

        if (cookie.load('token')) {

            fetch("/chats", {
                method: 'GET',
                headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
            })
                .then(response => response.json())
                .then(resData => {
                    cookie.save("chats", resData, {path: "/"});

                    // console.log("RES data " + resData)
                    //
                    // console.log("res data lenght " + resData.length)
                    //
                    // console.log("cookie.load(\"chats\")[0] " + cookie.load("chats")[0]["id"])

                    if (resData !== undefined && resData.length > 0) {
                        //console.log("condition")
                        this.setState({path: '/chat/' + cookie.load("chats")[0]["id"]})
                        //console.log("condition state path " + this.state.path)
                    } else {
                        this.setState({path: '/'})
                    }
                })
        }
    }

    render () {

        console.log("this.state.path "+ this.state.path)

        return(<Redirect to={{
            pathname: this.state.path
        }}
        />)

    }
}

export default Chats