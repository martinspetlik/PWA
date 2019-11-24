import {Component} from "react";
import cookie from "react-cookies";
import Profile from "./Profile";
import React from "react";

class GoogleLogin extends Component {
    constructor() {
        super()
        this.state = {
            name: '',
            email: ''
        }
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

                    test
                    </div>
                </div>
            </div>
        )
    }
}
export default GoogleLogin
