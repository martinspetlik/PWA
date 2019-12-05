import {Component} from "react";
import cookie from "react-cookies";
import React from "react";
import {login} from "./UserFunctions";
import {AlertDanger, AlertPrimary} from "./Alerts";

class PasswordReset extends Component {
    constructor() {
        super()
        this.state = {
            email: '',
            password: '',
            message: '',
            resetToken: ''
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

        fetch("/reset/" + this.state.resetToken, {
            method: 'POST',
            // mode: 'no-cors',

            headers: new Headers({
                'Content-Type': 'application/json'}),

            body: JSON.stringify({
                email: this.state.email,
                password: this.state.password
            }),

        })
            .then(response => response.json())
            .then(res => {
                if (res.success) {
                    this.setState({message: AlertPrimary(res.message)});


                    setTimeout(function () {
                        console.log('after');
                    }, 3000);


                    //this.props.history.push("/")

                } else {
                    this.setState({message: AlertDanger(res.message)});
                }

            });
    }

    componentDidMount() {

        var path = this.props.location.pathname.split("/")
        var resetToken = path[path.length-1]

        this.setState({resetToken: resetToken});

        fetch("/reset/" + resetToken, {
            method: 'GET',
            mode: 'no-cors'
        })
            .then(response => response.json())
            .then(resData => {
                if (resData.success) {
                    this.setState({email: resData.email});
                } else {
                    this.setState({message: AlertDanger(resData.message)});
                }
                console.log(JSON.stringify(resData))

            })
    }

    render () {

        return (
            <div className="container">
                <div className="row">
                    <div className="col-md-6 mt-5 mx-auto">
                        {this.state.message}
                        <form noValidate onSubmit={this.onSubmit}>
                            <h1 className="h3 mb-3 font-weight-normal">Password reset</h1>
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
                                    placeholder="Enter new password"
                                    value={this.state.password}
                                    onChange={this.onChange}
                                    required />
                            </div>

                            <button type="submit" className="btn btn-lg btn-primary btn-block">
                                Send reset link to email
                            </button>
                        </form>

                    </div>
                </div>
            </div>
        )
    }
}
export default PasswordReset