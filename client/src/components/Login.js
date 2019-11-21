import React, { Component } from 'react'
import { login } from './UserFunctions'
import {AlertDanger} from "./Alerts";

import cookie from 'react-cookies';
import {Redirect} from "react-router-dom";

class Login extends Component {
    constructor() {
        super()
        this.state = {
            email: '',
            password: '',
            message: ''
        }


        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }


    onSubmit (e) {
        e.preventDefault()

        const user = {
            email: this.state.email,
            password: this.state.password
        }
        //const [cookies, setCookie] = useCookies(['chat']);

        login(user).then(res => {
            console.log(res)

            if (res.success) {
                cookie.save("token", res.access_token, {path: "/", HttpOnly:true});
                cookie.save("current_user_name", res.user_name, {path: "/", HttpOnly:true});

            } else {

                this.state.email = ""
                this.state.password = ""
                this.setState({ message: AlertDanger(res.message) });
                return false
            }
        })

        this.getChats()

        Object.keys(cookie.load("chats")).map(key => (
            this.props.history.push("/chat/" + key)
        ))



    }

    getChats() {
        //console.log(cookie.load('token'))
        if (cookie.load('token')) {

            fetch("http://localhost:3000/chats", {
                method: 'GET',
                headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
            })
                .then(response => response.json())
                .then(resData => {
                    cookie.save("chats", resData, {path: "/"});
                })
        }
    }

    render () {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-md-6 mt-5 mx-auto">

                        {this.state.message}

                        <form noValidate onSubmit={this.onSubmit}>
                            <h1 className="h3 mb-3 font-weight-normal">Please sign in</h1>
                            <div className="form-group">
                                <label htmlFor="email">Email Address</label>
                                <input type="email"
                                    className="form-control"
                                    name="email"
                                    placeholder="Enter Email"
                                    value={this.state.email}
                                    onChange={this.onChange} />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">Password </label>
                                <input type="password"
                                    className="form-control"
                                    name="password"
                                    placeholder="Enter Password"
                                    value={this.state.password}
                                    onChange={this.onChange} />
                            </div>

                            <button type="submit" className="btn btn-lg btn-primary btn-block">
                                Sign in
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        )
    }
}

export default Login