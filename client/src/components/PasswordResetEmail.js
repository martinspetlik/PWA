import {Component} from "react";
import cookie from "react-cookies";
import React from "react";
import {login} from "./UserFunctions";
import {AlertDanger, AlertPrimary} from "./Alerts";

class PasswordResetEmail extends Component {
    constructor() {
        super()
        this.state = {
            name: '',
            email: ''
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
        }

        fetch("/reset", {
            method: 'POST',
            // mode: 'no-cors',
            headers: new Headers({
                'Content-Type': 'application/json'}),

            body: JSON.stringify({
                email: this.state.email,
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



    // componentDidMount() {
    //
    //     // fetch("http://localhost:3000/login", {
    //     //     method: 'GET',
    //     //     mode: 'no-cors'
    //     // })
    //         // .then(response => response.json())
    //         // .then(resData => {
    //         //     console.log(JSON.stringify(resData))
    //         //
    //         // })
    //
    // }

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
export default PasswordResetEmail