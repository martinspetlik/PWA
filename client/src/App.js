import React, { Component } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom'

import NavBar from './components/NavBar'
import Landing from './components/Landing'
import Login from './components/Login'
import Register from './components/Register'
import Profile from './components/Profile'
import Chat from './components/Chat'
import PasswordResetEmail from './components/PasswordResetEmail'
import PasswordReset from './components/PasswordReset'
import ChatAdd from './components/ChatAdd'
import Chats from './components/Chats'
import Logout from './components/Logout'


class App extends Component {

  render () {
    return (
      <Router>
        <div className="App">
          <NavBar />
          <Route exact path="/" component={Landing} />
            <Route exact path="/registration" component={Register} />
            <Route exact path="/logout" component={Logout} />
            <Route exact path="/reset" component={PasswordResetEmail} />
            <Route exact path="/reset/:token" component={PasswordReset} />
            <Route exact path="/" component={Login} />
            <Route exact path="/profile" component={Profile} />
            <Route exact path="/chat/:id" component={Chat} />
            <Route exact path="/chats/add" component={ChatAdd} />
            <Route exact path="/chats" component={Chats} />
        </div>
      </Router>
    );
  }
}

export default App;
