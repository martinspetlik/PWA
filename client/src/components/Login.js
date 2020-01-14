import React, { Component } from 'react'
import { login } from './UserFunctions'
import {AlertDanger} from "./Alerts";
import { Link } from 'react-router-dom';
import cookie from 'react-cookies';


class Login extends Component {
    constructor(props) {
        super(props)
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

    componentDidMount() {
        const params = new URLSearchParams(this.props.location.search);
        const token = params.get('token');

        if (token !== null) {
            this.props.history.push("/reset/" + token)
        }
    }


    onSubmit (e) {
        e.preventDefault()

        const user = {
            email: this.state.email,
            password: this.state.password
        }

        login(user).then(res => {
            console.log("res " + res)
            if (res.success) {
                cookie.save("token", res.access_token, {path: "/", HttpOnly:true});
                cookie.save("current_user_name", res.user_name, {path: "/", HttpOnly:true});

                this.getChats()

                if (cookie.load("chats") === undefined) {
                    this.props.history.push("/chats")
                } else {
                    if (cookie.load("chats").length === 0) {
                        this.props.history.push("/chats")
                    }
                    Object.keys(cookie.load("chats")).map(key => (
                        this.props.history.push("/chat/" + cookie.load("chats")[key]["id"])
                    ))
                }

            } else {

                this.state.email = ""
                this.state.password = ""
                this.setState({ message: AlertDanger(res.message) });
                return false
            }
        })


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


                        <Link to="/reset" > Reset password </Link>
                    </div>
                </div>
            </div>
        )
    }
}

export default Login