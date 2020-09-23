import React, { useState, Component } from 'react';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { Box } from '@material-ui/core';
import IconButton from '@material-ui/core/IconButton';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import InputAdornment from '@material-ui/core/InputAdornment';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Visibility from '@material-ui/icons/Visibility';
import VisibilityOff from '@material-ui/icons/VisibilityOff';

export default class Login extends Component{
  constructor(props){
      super(props);
      this.state={
          email:'',
          password:'',
          isSubmitted: false,
          hasEmailError: false,
          hasPassError: false,
          showPassword: false,
          canSubmit: false,
        };
  }

  handleChange = (prop) => (event) => {
    this.setState({[prop]: event.target.value });
  };

  handleClickShowPassword = () => {
    this.setState({showPassword: !this.state.showPassword });
  };

  handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  handleClickisSubmitted = () => {
    this.setState({isSubmitted: !this.state.isSubmitted });
    
    sessionStorage.setItem('key', 'value');
  }

  isEmptyEmail = () => {
    if(this.state.username === ''){
      this.setState({hasEmailError: true});
    }else{
      this.setState({hasEmailError: false});
    }
  }

  isEmptyPass = () => {
    if(this.state.username === ''){
      this.setState({hasPassError: true});
    }else{
      this.setState({hasPassError: false});
    }
  }


  render(){
    return (
      <div className='loginpage'>
          <br /><br />
        <Typography variant="h2" gutterBottom>
          Login
        </Typography>
        <br /><br />
        <Box textAlign="center">
          <form className='form' noValidate autoComplete="off">
          <TextField 
            id="standard-basic" 
            label="Email"
            onChange={this.handleChange('email')}
            onBlur={this.isEmptyEmail}
          />
          {this.state.hasEmailError ?
            <FormHelperText id="component-error-text">
              Email is required.
            </FormHelperText> : <br />}
          <br />

          <FormControl className="passform">
            <InputLabel htmlFor="standard-adornment-password">Password</InputLabel>
            <Input
              id="standard-adornment-password"
              type={this.state.showPassword ? 'text' : 'password'}
              value={this.state.password}
              onChange={this.handleChange('password')}
              onBlur={this.isEmptyPass}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={this.handleClickShowPassword}
                    onMouseDown={this.handleMouseDownPassword}
                  >
                    {this.state.showPassword ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </InputAdornment>
              }
            />
            {this.state.hasPassError ?
            <FormHelperText id="component-error-text">
              Password is required.
            </FormHelperText> : <br />}
          </FormControl>

              <br /><br />
          <FormControl error className="passform-error" color="secondary">
            <InputLabel htmlFor="component-error">Password</InputLabel>
            <Input
              id="standard-adornment-password"
              type={this.state.showPassword ? 'text' : 'password'}
              value={this.state.password}
              onChange={this.handleChange('password')}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={this.handleClickShowPassword}
                    onMouseDown={this.handleMouseDownPassword}
                  >
                    {this.state.showPassword ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </InputAdornment>
              }
            />
            <FormHelperText id="component-error-text">Error: Passwords do not match.</FormHelperText>
          </FormControl>

      </form>
      <br /><br /><br />
      <Button className='button' variant="contained" color="primary" href="/user"
              onClick={this.handleClickisSubmitted}>
          Login
      </Button>
      {/* space */}　{/* space */}
      <Button className='button' variant="contained" color="primary" href="/signup">
          Signup
      </Button>
      <br /><br /><br />
      </Box>
      </div>
    );
  }
}
