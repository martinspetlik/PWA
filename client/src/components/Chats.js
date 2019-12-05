import React, { Component } from 'react'
import cookie from 'react-cookies';

import { Redirect } from 'react-router-dom'
import Avatar from 'react-avatar';


class Chats extends Component {
    constructor() {
        super()
        this.state = {
            message: '',
            path: ''
        }

        this.onSubmitAdd = this.onSubmitAdd.bind(this)
    }

    getChats() {
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
                        console.log("condition")
                        this.setState({path: '/chat/' + cookie.load("chats")[0]["id"]})
                        //console.log("condition state path " + this.state.path)
                    } else {
                        console.log("to homepage")
                        this.setState({path: '/'})
                    }
                })
        }
    }

    onSubmitAdd(e) {
        e.preventDefault()
        this.props.history.push("/chats/add")
    }

    componentDidMount(){
        this.getChats()
    }

    // renderData() {
    //     if (this.state.path.length === 0) {
    //         console.log("DIV")
    //         return ()
    //
    //     } else {
    //         console.log("REDIRECT")
    //         //return <Redirect to={{pathname: this.state.path}}/>
    //     }
    // }

    render () {

        console.log("this.state.path "+ this.state.path)


        return(<div id="frame">
                <div id="sidepanel">
                    <div id="profile">
                        <div className="wrap">
                            <Avatar name={cookie.load("current_user_name")} className="avatar" size="50px"/>
                            <p>{cookie.load("current_user_name")}</p>
                        </div>
                    </div>
                    <div id="contacts">
                        <ul>
                        </ul>
                    </div>
                    <div id="bottom-bar">
                        <form onSubmit={this.onSubmitAdd}>
                        <button id="addcontact" ><i className="fa fa-plus-square fa-fw" aria-hidden="true"></i> <span>Add chat</span>
                        </button>
                        </form>
                    </div>
                </div>
                <div className="content">
                    <div className="messages">
                        <ul id="all_messages">
                        </ul>
                    </div>

                    <div className="message-input">
                        <div className="wrap">
                             </div>
                    </div>
                </div>
            </div>

        )

    }
}

export default Chats