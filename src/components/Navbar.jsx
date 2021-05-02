import React from 'react';
import PropTypes from 'prop-types';

const Navbar = ({ userID }) => (
  <div>
    {/* eslint-disable jsx-a11y/anchor-is-valid, */}
    <ul className="nav nav-pills p-1 navbar-dark bg-dark">
      <span className="navbar-brand m-1 h1">NJ COURT PROJECT</span>
      <a href="/" className="nav-link h4">Home</a>
      <li className="nav-item dropdown ml-auto">
        <a href="#" className="nav-link dropdown-toggle h4" data-toggle="dropdown">User ID</a>
        <div className="dropdown-menu dropdown-menu-right" disabled>
          <p className="dropdown-item">Unique User ID:</p>
          <div className="dropdown-divider" />
          <h6 className="dropdown-item">{userID}</h6>
        </div>
      </li>
    </ul>
    {/* eslint-disable react/no-array-index-key */}
  </div>
);

Navbar.propTypes = {
  userID: PropTypes.string.isRequired,
};

export default Navbar;
