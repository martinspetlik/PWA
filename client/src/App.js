import React, { Component } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom'

import NavBar from './components/NavBar'
import Landing from './components/Landing'
import Login from './components/Login'
import Register from './components/Register'
import Profile from './components/Profile'
import Chat from './components/Chat'
import GoogleLogin from './components/GoogleLogin'

class App extends Component {
  render () {
    return (
      <Router>
        <div className="App">
          <NavBar />
          <Route exact path="/" component={Landing} />
            <Route exact path="/registration" component={Register} />
            <Route exact path="/" component={Login} />
            {/*<Route exact path="/login" component={GoogleLogin} />*/}
            <Route exact path="/profile" component={Profile} />
            <Route exact path="/chat/:id" component={Chat} />
        </div>
      </Router>
    );
  }
}

export default App;
